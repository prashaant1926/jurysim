'use client';

import { useEffect, useState, useRef } from 'react';
import { DeliberationConfig } from '@/app/deliberation/page';

type Props = {
  sessionId: string;
  config: DeliberationConfig;
  onReset: () => void;
};

type JurorStatement = {
  juror_id: number;
  juror_name: string;
  content: string;
  phase: string;
  timestamp: string;
  sentiment?: string;
};

type Vote = {
  juror_id: number;
  juror_name: string;
  verdict: string;
  confidence: number;
  reasoning: string;
  round_number: number;
};

type DeliberationState = {
  phase: string;
  statements: JurorStatement[];
  votes: Vote[];
  final_verdict?: string;
  is_complete: boolean;
  vote_counts?: {
    guilty: number;
    not_guilty: number;
    undecided: number;
  };
  jurors: Array<{id: number; name: string}>;
  partialStatements: Map<number, string>;
};

export function DeliberationView({ sessionId, config, onReset }: Props) {
  const [state, setState] = useState<DeliberationState>({
    phase: 'starting',
    statements: [],
    votes: [],
    is_complete: false,
    jurors: [],
    partialStatements: new Map()
  });
  const [isConnected, setIsConnected] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Connecting to deliberation room...');
  const scrollRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Connect to SSE endpoint
    const eventSource = new EventSource(`http://localhost:8000/api/v1/deliberations/deliberations/${sessionId}/stream`);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      setStatusMessage('Connected! Jury is assembling...');
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'status') {
        setStatusMessage(data.data.message);
        setState(prev => ({
          ...prev,
          phase: data.data.phase
        }));
      } else if (data.type === 'jurors') {
        setState(prev => ({
          ...prev,
          jurors: data.data
        }));
      } else if (data.type === 'partial_statement') {
        setState(prev => {
          const newPartials = new Map(prev.partialStatements);
          newPartials.set(data.data.juror_id, data.data.content);
          return {
            ...prev,
            partialStatements: newPartials
          };
        });
      } else if (data.type === 'statement') {
        setState(prev => {
          const newPartials = new Map(prev.partialStatements);
          newPartials.delete(data.data.juror_id);
          return {
            ...prev,
            statements: [...prev.statements, data.data],
            phase: data.data.phase,
            partialStatements: newPartials
          };
        });
        setStatusMessage('Deliberation in progress...');
      } else if (data.type === 'vote') {
        setState(prev => ({
          ...prev,
          votes: [...prev.votes, data.data]
        }));
      } else if (data.type === 'vote_summary') {
        setState(prev => ({
          ...prev,
          vote_counts: data.data
        }));
      } else if (data.type === 'complete') {
        setState(prev => ({
          ...prev,
          is_complete: true,
          final_verdict: data.data.verdict
        }));
      }
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [sessionId]);

  useEffect(() => {
    // Auto-scroll to bottom when new content arrives
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [state.statements]);

  const getPhaseDisplay = () => {
    switch (state.phase) {
      case 'opening': return 'Opening Statements';
      case 'evidence_review': return 'Evidence Review';
      case 'discussion': return 'General Discussion';
      case 'voting': return 'Voting';
      case 'final_verdict': return 'Final Verdict';
      default: return 'Starting...';
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'guilty': return 'text-red-600';
      case 'not_guilty': return 'text-green-600';
      case 'undecided': return 'text-text-muted';
      default: return 'text-text-secondary';
    }
  };

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case 'assertive': return 'bg-red-50 border-red-100';
      case 'agreeable': return 'bg-green-50 border-green-100';
      case 'challenging': return 'bg-orange-50 border-orange-100';
      case 'neutral': return 'bg-gray-50 border-gray-100';
      default: return 'bg-white border-border-light';
    }
  };

  return (
    <div className="container mx-auto py-24">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-t-2xl shadow-lg px-12 py-8 border-b border-border-light">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="mb-2">{config.case.case_title}</h2>
              <p className="text-text-secondary">{config.county}, {config.state}</p>
            </div>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-text-secondary">{isConnected ? 'Connected' : 'Disconnected'}</span>
              </div>
              <button
                onClick={onReset}
                className="px-6 py-3 text-text-primary hover:text-primary border-b-2 border-transparent hover:border-primary transition-all"
              >
                New Deliberation
              </button>
            </div>
          </div>
        </div>

        {/* Current Phase */}
        <div className="bg-background border-b border-border-light px-12 py-6">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-sm font-medium text-primary uppercase tracking-wider">Current Phase</span>
              <h3 className="mt-1">{getPhaseDisplay()}</h3>
            </div>
            {state.vote_counts && (
              <div className="flex gap-8 text-lg">
                <span className="text-red-600 font-medium">Guilty: {state.vote_counts.guilty}</span>
                <span className="text-green-600 font-medium">Not Guilty: {state.vote_counts.not_guilty}</span>
                {state.vote_counts.undecided > 0 && (
                  <span className="text-text-muted font-medium">Undecided: {state.vote_counts.undecided}</span>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Deliberation Content */}
        <div 
          ref={scrollRef}
          className="h-[600px] overflow-y-auto bg-white rounded-b-2xl shadow-lg p-12"
        >
          <div className="space-y-6">
            {/* Show status message when no content yet */}
            {state.statements.length === 0 && (
              <div className="text-center py-32">
                <div className="inline-flex items-center space-x-3 text-text-secondary mb-4">
                  <svg className="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="text-lg">{statusMessage}</span>
                </div>
                <p className="text-text-muted">The foreperson is being selected and jurors are taking their seats...</p>
              </div>
            )}
            
            {state.statements.map((statement, index) => (
              <div
                key={index}
                className={`p-8 rounded-xl border transition-all ${getSentimentColor(statement.sentiment)}`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className="font-medium text-lg text-text-primary">{statement.juror_name}</span>
                    <span className="text-sm text-text-muted ml-4">
                      {new Date(statement.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  {statement.sentiment && (
                    <span className="text-xs font-medium bg-white px-3 py-1.5 rounded-full text-text-secondary border border-border-light">
                      {statement.sentiment}
                    </span>
                  )}
                </div>
                <p className="text-text-secondary leading-relaxed">{statement.content}</p>
              </div>
            ))}
            
            {/* Show partial statements (jurors currently speaking) */}
            {Array.from(state.partialStatements.entries()).map(([jurorId, content]) => {
              const juror = state.jurors.find(j => j.id === jurorId);
              return (
                <div
                  key={`partial-${jurorId}`}
                  className="p-8 rounded-xl border border-primary/20 bg-orange-50/50 animate-pulse"
                >
                  <div className="flex items-start mb-4">
                    <span className="font-medium text-lg text-text-primary">{juror?.name || `Juror ${jurorId}`}</span>
                    <span className="text-sm text-primary ml-4 flex items-center">
                      <svg className="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      speaking...
                    </span>
                  </div>
                  <p className="text-text-secondary italic leading-relaxed">{content}</p>
                </div>
              );
            })}

            {/* Show votes when in voting phase */}
            {state.phase === 'voting' && state.votes.length > 0 && (
              <div className="mt-8 p-10 bg-gray-50 rounded-xl">
                <h3 className="mb-6">Voting Round {state.votes[state.votes.length - 1].round_number}</h3>
                <div className="space-y-4">
                  {state.votes
                    .filter(v => v.round_number === state.votes[state.votes.length - 1].round_number)
                    .map((vote, index) => (
                      <div key={index} className="flex items-start gap-6 p-4 bg-white rounded-lg">
                        <span className="font-medium min-w-[140px] text-text-primary">{vote.juror_name}:</span>
                        <span className={`font-semibold text-lg ${getVerdictColor(vote.verdict)}`}>
                          {vote.verdict.replace('_', ' ').toUpperCase()}
                        </span>
                        <span className="text-sm text-text-muted">({Math.round(vote.confidence * 100)}%)</span>
                        <span className="text-text-secondary italic flex-1">{vote.reasoning}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Final Verdict */}
            {state.is_complete && (
              <div className="mt-12 p-16 bg-text-primary text-white rounded-xl text-center">
                <h2 className="text-white mb-6">VERDICT</h2>
                {state.final_verdict ? (
                  <p className="text-5xl font-bold">
                    {state.final_verdict === 'guilty' ? 'GUILTY' : 
                     state.final_verdict === 'not_guilty' ? 'NOT GUILTY' : 
                     'HUNG JURY'}
                  </p>
                ) : (
                  <p className="text-3xl">Hung Jury - No Unanimous Verdict Reached</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}