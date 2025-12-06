'use client';

import { useEffect, useState } from 'react';

export function LoadingDeliberation() {
  const [currentStep, setCurrentStep] = useState(0);
  const [dots, setDots] = useState('');

  const steps = [
    'Loading case files...',
    'Analyzing evidence documents...',
    'Selecting jury pool...',
    'Generating juror profiles...',
    'Assigning personality traits...',
    'Creating deliberation room...',
    'Selecting foreperson...',
    'Initializing AI agents...',
    'Starting deliberation...'
  ];

  useEffect(() => {
    // Progress through steps
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 2000);

    // Animate dots
    const dotsInterval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 500);

    return () => {
      clearInterval(stepInterval);
      clearInterval(dotsInterval);
    };
  }, []);

  return (
    <div className="container mx-auto py-24">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-16 text-center">
          <h1 className="mb-16">Assembling Your Virtual Jury</h1>
          
          <div className="space-y-8 mb-20">
            {steps.map((step, index) => (
              <div
                key={index}
                className={`flex items-center justify-center space-x-6 transition-all duration-500 ${
                  index <= currentStep ? 'opacity-100' : 'opacity-30'
                }`}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                  index < currentStep 
                    ? 'bg-green-500 text-white animate-none' 
                    : index === currentStep 
                    ? 'bg-primary text-white animate-pulse' 
                    : 'bg-border-light text-text-muted'
                }`}>
                  {index < currentStep ? '✓' : index + 1}
                </div>
                <span className={`text-lg ${
                  index === currentStep 
                    ? 'font-semibold text-text-primary' 
                    : 'font-normal text-text-secondary'
                }`}>
                  {step}{index === currentStep && dots}
                </span>
              </div>
            ))}
          </div>

          <div className="p-12 bg-background rounded-xl mb-16">
            <h3 className="mb-6">What's happening behind the scenes?</h3>
            <p className="text-text-secondary leading-relaxed max-w-3xl mx-auto">
              The system is creating a realistic jury of 6 people based on demographic data from your selected county. 
              Each juror is being assigned personality traits, backgrounds, and deliberation styles that reflect real jury behavior. 
              This process ensures authentic and diverse perspectives in your simulation.
            </p>
          </div>

          <div className="text-center">
            <div className="inline-flex items-center space-x-4 px-8 py-4 bg-background rounded-full border border-border-light">
              <svg className="animate-spin h-6 w-6 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="font-medium text-primary text-lg">
                This may take 15-30 seconds
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}