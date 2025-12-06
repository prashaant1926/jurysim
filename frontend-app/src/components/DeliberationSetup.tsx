'use client';

import { useState } from 'react';
import { DeliberationConfig, Case } from '@/app/deliberation/page';

type Props = {
  onStart: (config: DeliberationConfig) => void;
};

const PRESET_CASES = [
  {
    value: 'oj_simpson',
    label: 'O.J. Simpson Murder Trial',
    case: {
      case_type: 'murder',
      case_title: 'People of the State of California v. Orenthal James Simpson',
      summary: 'Former NFL star and actor O.J. Simpson is charged with the murders of his ex-wife Nicole Brown Simpson and Ronald Goldman on June 12, 1994. The victims were found dead outside Nicole\'s condominium in Brentwood, Los Angeles.',
      key_evidence: [
        'Blood evidence: Simpson\'s blood found at crime scene, victims\' blood in Bronco and at Rockingham estate',
        'Hair and fiber evidence matching Simpson found on victims and at crime scene',
        'Bloody glove found at Bundy crime scene, matching glove found at Simpson\'s Rockingham estate',
        'Size 12 Bruno Magli shoe prints at crime scene (Simpson wears size 12)',
        'History of domestic violence: Multiple 911 calls and police reports documenting abuse',
        'No alibi: Simpson\'s whereabouts unaccounted for during time of murders',
        'Cuts on Simpson\'s left hand observed by police night of murders',
        'DNA evidence: Multiple DNA matches linking Simpson to crime scene and victims',
        'Limousine driver testimony: Saw Simpson entering house at 10:55 PM',
        'Flight in white Bronco and apparent suicide note'
      ],
      prosecution_argument: 'The evidence overwhelmingly proves Simpson murdered Nicole Brown Simpson and Ronald Goldman. His history of domestic violence shows motive, his blood at the scene and victims\' blood at his home prove his presence, and the matching gloves and shoe prints confirm his involvement. The DNA evidence alone proves guilt beyond reasonable doubt.',
      defense_argument: 'Simpson was framed by a racist LAPD. The blood evidence was contaminated or planted, the glove doesn\'t fit, and the timeline makes it impossible for Simpson to have committed the murders. Detective Mark Fuhrman\'s racist comments show police bias and evidence tampering.',
      jury_instructions: 'You must find the defendant guilty beyond a reasonable doubt. Consider all evidence including DNA, blood evidence, and witness testimony. You may consider evidence of domestic violence as it relates to motive. If you have reasonable doubt about any element of the crime, you must acquit.'
    }
  },
  {
    value: 'zimmerman',
    label: 'George Zimmerman Trial',
    case: {
      case_type: 'murder',
      case_title: 'State of Florida v. George Zimmerman',
      summary: 'George Zimmerman, a neighborhood watch volunteer, is charged with second-degree murder in the shooting death of 17-year-old Trayvon Martin on February 26, 2012, in Sanford, Florida. Martin was walking back from a convenience store when the confrontation occurred.',
      key_evidence: [
        '911 call: Zimmerman reported Martin as suspicious, was told "we don\'t need you to follow him"',
        'Witness testimony: Conflicting accounts of who was on top during struggle',
        'Zimmerman\'s injuries: Broken nose, lacerations on back of head',
        'Martin was unarmed, carrying only Skittles and iced tea',
        'Gunshot wound: Contact shot to Martin\'s chest, indicating close proximity',
        'Zimmerman\'s statements: Claims Martin attacked him and he feared for his life',
        'No eyewitnesses to start of confrontation',
        'Rachel Jeantel testimony: Was on phone with Martin, heard initial exchange',
        'Expert testimony on whose voice was screaming for help on 911 call',
        'Zimmerman did not testify at trial'
      ],
      prosecution_argument: 'Zimmerman profiled, pursued, and confronted Martin based on unfounded suspicions. He was the aggressor who created the dangerous situation. His injuries were minor and did not justify use of deadly force. Martin was simply walking home and had every right to be there.',
      defense_argument: 'Zimmerman acted in self-defense when Martin attacked him, breaking his nose and slamming his head on concrete. He reasonably feared death or great bodily harm. He had a legal right to be where he was and to defend himself when attacked.',
      jury_instructions: 'If Zimmerman was not engaged in unlawful activity and was attacked in a place where he had a right to be, he had no duty to retreat and had the right to stand his ground and use deadly force if he reasonably believed it necessary to prevent death or great bodily harm. The danger need not have been actual; Zimmerman\'s belief of danger must have been reasonable.'
    }
  },
  {
    value: 'theft',
    label: 'Theft Case',
    case: {
      case_type: 'theft',
      case_title: 'State v. Johnson',
      summary: 'Defendant accused of shoplifting electronics from a retail store.',
      key_evidence: [
        'Security camera footage showing defendant in store',
        'Receipt showing no purchase of missing items',
        'Witness testimony from store employee'
      ],
      prosecution_argument: 'Video evidence clearly shows defendant concealing items and leaving without paying.',
      defense_argument: 'Video quality is poor and defendant intended to pay but forgot items in cart.',
      jury_instructions: 'To convict of theft, you must find beyond reasonable doubt that defendant intentionally took property without permission.'
    }
  },
  {
    value: 'assault',
    label: 'Assault Case',
    case: {
      case_type: 'assault',
      case_title: 'State v. Smith',
      summary: 'Defendant accused of assault during a bar fight.',
      key_evidence: [
        'Medical records showing victim injuries',
        'Three witness testimonies with conflicting accounts',
        'Defendant\'s prior arrest record'
      ],
      prosecution_argument: 'Multiple witnesses saw defendant throw the first punch causing serious injuries.',
      defense_argument: 'Defendant acted in self-defense after being threatened by victim.',
      jury_instructions: 'Self-defense is justified if defendant reasonably believed force was necessary to prevent harm.'
    }
  },
  {
    value: 'murder',
    label: 'Murder Case',
    case: {
      case_type: 'murder',
      case_title: 'State v. Williams',
      summary: 'Defendant accused of first-degree murder of business partner.',
      key_evidence: [
        'DNA evidence at crime scene',
        'Financial records showing motive',
        'Alibi witness testimony',
        'Murder weapon not recovered'
      ],
      prosecution_argument: 'DNA evidence and clear financial motive prove defendant committed premeditated murder.',
      defense_argument: 'DNA could have been planted, alibi witness confirms defendant was elsewhere.',
      jury_instructions: 'First-degree murder requires premeditation and deliberate intent to kill.'
    }
  },
  {
    value: 'custom',
    label: 'Custom Case',
    case: null
  }
];

const COUNTIES = [
  { value: 'San Francisco', state: 'CA', label: 'San Francisco, CA (Liberal)' },
  { value: 'Maricopa', state: 'AZ', label: 'Maricopa, AZ (Purple/Swing)' },
  { value: 'Oklahoma', state: 'OK', label: 'Oklahoma, OK (Conservative)' },
  { value: 'Cook', state: 'IL', label: 'Cook County, IL (Chicago)' },
  { value: 'Harris', state: 'TX', label: 'Harris County, TX (Houston)' },
  { value: 'Miami-Dade', state: 'FL', label: 'Miami-Dade, FL (Miami)' },
  { value: 'King', state: 'WA', label: 'King County, WA (Seattle)' },
  { value: 'Orange', state: 'CA', label: 'Orange County, CA (Southern CA)' },
  { value: 'Fulton', state: 'GA', label: 'Fulton County, GA (Atlanta)' },
  { value: 'Dallas', state: 'TX', label: 'Dallas County, TX (Dallas)' }
];

export function DeliberationSetup({ onStart }: Props) {
  const [selectedCase, setSelectedCase] = useState('oj_simpson');
  const [selectedCounty, setSelectedCounty] = useState('San Francisco');
  const [customCase, setCustomCase] = useState<Case>({
    case_type: 'other',
    case_title: '',
    summary: '',
    key_evidence: [''],
    prosecution_argument: '',
    defense_argument: '',
    jury_instructions: ''
  });

  const handleAddEvidence = () => {
    setCustomCase({
      ...customCase,
      key_evidence: [...customCase.key_evidence, '']
    });
  };

  const handleRemoveEvidence = (index: number) => {
    setCustomCase({
      ...customCase,
      key_evidence: customCase.key_evidence.filter((_, i) => i !== index)
    });
  };

  const handleEvidenceChange = (index: number, value: string) => {
    const newEvidence = [...customCase.key_evidence];
    newEvidence[index] = value;
    setCustomCase({
      ...customCase,
      key_evidence: newEvidence
    });
  };

  const handleSubmit = () => {
    const county = COUNTIES.find(c => c.value === selectedCounty)!;
    const presetCase = PRESET_CASES.find(c => c.value === selectedCase);
    
    const caseToUse = selectedCase === 'custom' ? customCase : presetCase!.case!;
    
    // Validate custom case
    if (selectedCase === 'custom') {
      if (!customCase.case_title || !customCase.summary || 
          customCase.key_evidence.filter(e => e.trim()).length === 0 ||
          !customCase.prosecution_argument || !customCase.defense_argument) {
        alert('Please fill in all required fields for custom case');
        return;
      }
    }

    onStart({
      county: county.value,
      state: county.state,
      case: caseToUse
    });
  };

  return (
    <div className="container mx-auto py-24">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-center mb-16">Configure Your Deliberation</h1>
        
        <div className="bg-white rounded-2xl shadow-lg p-12 space-y-12">
          {/* County Selection */}
          <div>
            <h3 className="mb-2">Select Jury Demographics</h3>
            <p className="text-gray-600 mb-6">
              Choose the county to simulate realistic jury composition and regional attitudes.
            </p>
            <select
              value={selectedCounty}
              onChange={(e) => setSelectedCounty(e.target.value)}
              className="w-full px-6 py-4 text-lg bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-all"
            >
              {COUNTIES.map(county => (
                <option key={county.value} value={county.value}>
                  {county.label}
                </option>
              ))}
            </select>
          </div>

          {/* Case Selection */}
          <div>
            <h3 className="mb-2">Select Case Study</h3>
            <p className="text-gray-600 mb-6">
              Choose from landmark cases or create your own custom scenario.
            </p>
            <select
              value={selectedCase}
              onChange={(e) => setSelectedCase(e.target.value)}
              className="w-full px-6 py-4 text-lg bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-all"
            >
              {PRESET_CASES.map(caseOption => (
                <option key={caseOption.value} value={caseOption.value}>
                  {caseOption.label}
                </option>
              ))}
            </select>
          </div>

          {/* Custom Case Form */}
          {selectedCase === 'custom' && (
            <div className="pt-8 border-t border-gray-100 space-y-8">
              <h2 className="text-2xl">Custom Case Details</h2>
              
              <div className="grid gap-8">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Case Title
                  </label>
                  <input
                    type="text"
                    value={customCase.case_title}
                    onChange={(e) => setCustomCase({ ...customCase, case_title: e.target.value })}
                    className="w-full px-5 py-3.5 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-all"
                    placeholder="e.g., State v. Doe"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Case Type
                  </label>
                  <select
                    value={customCase.case_type}
                    onChange={(e) => setCustomCase({ ...customCase, case_type: e.target.value })}
                    className="w-full px-5 py-3.5 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-all"
                  >
                    <option value="murder">Murder</option>
                    <option value="theft">Theft</option>
                    <option value="assault">Assault</option>
                    <option value="fraud">Fraud</option>
                    <option value="drug">Drug</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Case Summary
                  </label>
                  <textarea
                    value={customCase.summary}
                    onChange={(e) => setCustomCase({ ...customCase, summary: e.target.value })}
                    className="w-full px-5 py-3.5 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-all resize-none"
                    rows={4}
                    placeholder="Brief description of the case..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Key Evidence
                  </label>
                  <div className="space-y-3">
                    {customCase.key_evidence.map((evidence, index) => (
                      <div key={index} className="flex gap-3">
                        <input
                          type="text"
                          value={evidence}
                          onChange={(e) => handleEvidenceChange(index, e.target.value)}
                          className="flex-1 px-5 py-3.5 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-all"
                          placeholder={`Evidence ${index + 1}`}
                        />
                        {customCase.key_evidence.length > 1 && (
                          <button
                            onClick={() => handleRemoveEvidence(index)}
                            className="px-5 py-3.5 text-red-600 hover:bg-red-50 rounded-xl transition-all"
                          >
                            Remove
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={handleAddEvidence}
                    className="mt-4 px-5 py-2.5 text-primary hover:bg-orange-50 rounded-lg transition-all text-sm font-medium"
                  >
                    + Add Evidence
                  </button>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Prosecution Argument
                  </label>
                  <textarea
                    value={customCase.prosecution_argument}
                    onChange={(e) => setCustomCase({ ...customCase, prosecution_argument: e.target.value })}
                    className="w-full px-5 py-3.5 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-all resize-none"
                    rows={3}
                    placeholder="Main argument for guilt..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Defense Argument
                  </label>
                  <textarea
                    value={customCase.defense_argument}
                    onChange={(e) => setCustomCase({ ...customCase, defense_argument: e.target.value })}
                    className="w-full px-5 py-3.5 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-all resize-none"
                    rows={3}
                    placeholder="Main argument for innocence..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Jury Instructions
                  </label>
                  <textarea
                    value={customCase.jury_instructions}
                    onChange={(e) => setCustomCase({ ...customCase, jury_instructions: e.target.value })}
                    className="w-full px-5 py-3.5 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-all resize-none"
                    rows={3}
                    placeholder="Legal standards the jury must follow..."
                  />
                </div>
              </div>
            </div>
          )}

          {/* Preview for preset cases */}
          {selectedCase !== 'custom' && (
            <div className="p-8 bg-gray-50 rounded-xl">
              <h3 className="mb-4">Case Preview</h3>
              {PRESET_CASES.find(c => c.value === selectedCase)?.case && (
                <div className="space-y-3 text-gray-600">
                  <p><span className="font-medium text-gray-800">Title:</span> {PRESET_CASES.find(c => c.value === selectedCase)!.case!.case_title}</p>
                  <p><span className="font-medium text-gray-800">Summary:</span> {PRESET_CASES.find(c => c.value === selectedCase)!.case!.summary}</p>
                </div>
              )}
            </div>
          )}

          <button
            onClick={handleSubmit}
            className="w-full py-5 bg-primary hover:bg-primary-hover text-white font-medium text-lg rounded-xl transition-all transform hover:scale-[1.02] hover:shadow-xl flex items-center justify-center gap-3"
          >
            Begin Deliberation
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="inline-block">
              <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}