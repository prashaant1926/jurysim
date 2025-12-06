'use client';

import { useState } from 'react';
import { DeliberationSetup } from '@/components/DeliberationSetup';
import { DeliberationView } from '@/components/DeliberationView';
import { LoadingDeliberation } from '@/components/LoadingDeliberation';

export type Case = {
  case_type: string;
  case_title: string;
  summary: string;
  key_evidence: string[];
  prosecution_argument: string;
  defense_argument: string;
  jury_instructions: string;
};

export type DeliberationConfig = {
  county: string;
  state: string;
  case: Case;
};

export default function DeliberationPage() {
  const [config, setConfig] = useState<DeliberationConfig | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleStartDeliberation = async (deliberationConfig: DeliberationConfig) => {
    setConfig(deliberationConfig);
    setIsLoading(true);
    console.log('Starting deliberation with config:', deliberationConfig);
    
    try {
      // Start deliberation via API
      const response = await fetch('http://localhost:8000/api/v1/deliberations/deliberations/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          county: deliberationConfig.county,
          state: deliberationConfig.state,
          case: deliberationConfig.case,
        }),
      });

      console.log('Response status:', response.status);
      const responseText = await response.text();
      console.log('Response text:', responseText);

      if (!response.ok) {
        throw new Error(`Failed to start deliberation: ${response.status} ${responseText}`);
      }

      const data = JSON.parse(responseText);
      console.log('Session started:', data);
      setSessionId(data.session_id);
    } catch (error) {
      console.error('Error starting deliberation:', error);
      setIsLoading(false);
      alert(`Failed to start deliberation: ${error}. Make sure the backend is running on port 8000.`);
    }
  };

  const handleReset = () => {
    setConfig(null);
    setSessionId(null);
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen" style={{ background: '#F8F6F4' }}>
      {/* Header Section */}
      <div className="relative overflow-hidden">
        {/* Decorative Background Elements */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-20 right-20 w-64 h-64 rounded-full" style={{ background: 'linear-gradient(135deg, #FF6B35 0%, #F7461E 100%)' }}></div>
          <div className="absolute bottom-20 left-20 w-96 h-96 rounded-full" style={{ background: 'linear-gradient(135deg, #FF6B35 0%, #F7461E 100%)' }}></div>
        </div>

        <div className="container mx-auto px-16 py-24 relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            {/* Section Label */}
            <div className="section-label mb-8">
              JURY DELIBERATION SIMULATOR
            </div>

            {/* Main Title */}
            <h1 className="font-serif text-6xl font-medium mb-8" style={{ color: '#1E1E1E', lineHeight: '1.1' }}>
              Juries Don't Hear Facts.
              <br />
              They Hear Frames.
            </h1>

            {/* Subtitle */}
            <p className="text-xl mb-12 max-w-2xl mx-auto" style={{ color: '#666666' }}>
              Watch AI agents deliberate, disagree, and decide—so you can shape your 
              legal strategy with unprecedented clarity and insight.
            </p>

            {/* Status Indicator */}
            {!sessionId && !isLoading && (
              <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full border" style={{ backgroundColor: '#FFFFFF', borderColor: '#E5E5E0' }}>
                <div className="w-3 h-3 rounded-full animate-pulse" style={{ backgroundColor: '#FF6B35' }}></div>
                <span className="font-medium" style={{ color: '#1E1E1E' }}>Ready to Begin Deliberation</span>
              </div>
            )}

            {isLoading && !sessionId && (
              <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full border" style={{ backgroundColor: '#FFFFFF', borderColor: '#E5E5E0' }}>
                <div className="w-3 h-3 rounded-full animate-pulse" style={{ backgroundColor: '#FF6B35' }}></div>
                <span className="font-medium" style={{ color: '#1E1E1E' }}>Assembling Virtual Jury</span>
              </div>
            )}

            {sessionId && (
              <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full border" style={{ backgroundColor: '#FFFFFF', borderColor: '#E5E5E0' }}>
                <div className="w-3 h-3 rounded-full animate-pulse" style={{ backgroundColor: '#22C55E' }}></div>
                <span className="font-medium" style={{ color: '#1E1E1E' }}>Deliberation Active</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-16 pb-24">
        {!sessionId && !isLoading ? (
          <DeliberationSetup onStart={handleStartDeliberation} />
        ) : isLoading && !sessionId ? (
          <LoadingDeliberation />
        ) : sessionId ? (
          <DeliberationView 
            sessionId={sessionId}
            config={config!}
            onReset={handleReset}
          />
        ) : null}
      </div>

      {/* Footer Quote */}
      <div className="border-t" style={{ borderColor: '#E5E5E0', backgroundColor: '#FFFFFF' }}>
        <div className="container mx-auto px-16 py-12">
          <div className="text-center">
            <p className="text-lg italic font-serif" style={{ color: '#666666' }}>
              "The jury, passing on the prisoner's life, may in the sworn twelve have a thief or two 
              guiltier than him they try."
            </p>
            <p className="mt-2 text-sm font-medium" style={{ color: '#A8A8A8' }}>
              — William Shakespeare
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}