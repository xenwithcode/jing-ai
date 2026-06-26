import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import Hero from './components/Hero';
import UploadZone from './components/UploadZone';
import ProcessingView from './components/ProcessingView';
import ResultsView from './components/ResultsView';
import BudgetView from './components/BudgetView';
import ClientSignView from './components/ClientSignView';
import SignatureConfirmation from './components/SignatureConfirmation';
import ArtisanNotification from './components/ArtisanNotification';
import FinancialSummaryView from './components/FinancialSummaryView';
import type { DiagnosisResult, Budget, FinancialSummary } from './types';
import { generateBudget, generateFinancialSummary } from './services/api';
import toast from 'react-hot-toast';

type ViewType = 
  | 'hero' 
  | 'upload' 
  | 'processing' 
  | 'results' 
  | 'budget' 
  | 'client-sign' 
  | 'signature-confirmation'
  | 'financial-summary';

function AppPage() {
  const [searchParams] = useSearchParams();
  const initialView = searchParams.get('view') === 'upload' ? 'upload' : 'hero';
  const [currentView, setCurrentView] = useState<ViewType>(initialView);
  const [diagnosisResult, setDiagnosisResult] = useState<DiagnosisResult | null>(null);
  const [budget, setBudget] = useState<Budget | null>(null);
  const [financialSummary, setFinancialSummary] = useState<FinancialSummary | null>(null);
  const [signatureData, setSignatureData] = useState<{
    clientName: string;
    timestamp: string;
    budgetNumber: string;
    location?: { lat: number; lng: number };
  } | null>(null);
  const [showArtisanNotification, setShowArtisanNotification] = useState(false);

  const handleStartDiagnosis = () => setCurrentView('upload');

  const handleFileSelected = async (file: File, description: string) => {
    setCurrentView('processing');
    
    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('voice_text', description);
      
      const response = await fetch('/api/v1/diagnose', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (result.success) {
        setDiagnosisResult(result.data);
        setCurrentView('results');
      } else {
        toast.error('Diagnosis failed');
        setCurrentView('upload');
      }
    } catch (error) {
      console.error('API error:', error);
      toast.error('Connection error');
      setCurrentView('upload');
    }
  };

  const handleGenerateBudget = async () => {
    if (!diagnosisResult) return;

    try {
      const consolidated = diagnosisResult.consolidated_response;
      
      const budgetResponse = await generateBudget({
        diagnosis: consolidated.diagnosis,
        estimated_hours: 1.0,
        trade: 'plumber',
        urgency: consolidated.severity,
      });

      if (budgetResponse.success) {
        setBudget(budgetResponse.budget);
        setCurrentView('budget');
      } else {
        toast.error('Budget generation failed');
      }
    } catch (error) {
      console.error('Budget API error:', error);
      toast.error('Connection error');
    }
  };

  const handleSendToClient = () => {
    toast.success('Budget sent to client!');
    setTimeout(() => {
      setCurrentView('client-sign');
    }, 1000);
  };

  const handleClientSign = (data: {
    signature: string;
    timestamp: string;
    clientName: string;
    location?: { lat: number; lng: number };
  }) => {
    setSignatureData({
      clientName: data.clientName,
      timestamp: data.timestamp,
      budgetNumber: budget?.budget_metadata.budget_number || '',
      location: data.location,
    });
    setCurrentView('signature-confirmation');

    setTimeout(() => {
      setShowArtisanNotification(true);
      setTimeout(() => setShowArtisanNotification(false), 8000);
    }, 2000);
  };

  const handleCompleteJob = async () => {
    if (!budget) return;

    try {
      const summaryResponse = await generateFinancialSummary({
        budget: budget,
        actual_parts_cost: budget.cost_breakdown.parts_subtotal + 5,
        actual_hours: budget.cost_breakdown.labor.estimated_hours + 0.2,
        amount_charged: budget.cost_breakdown.total_rounded,
        client_name: budget.client_info.name,
        job_title: budget.budget_metadata.job_title,
        extra_costs: [
          {
            item: "Additional consumables",
            amount: 5.00,
            reason: "Extra Teflon tape and cleaning supplies",
          },
        ],
      });

      if (summaryResponse.success) {
        setFinancialSummary(summaryResponse.summary);
        setCurrentView('financial-summary');
      } else {
        toast.error('Failed to generate summary');
      }
    } catch (error) {
      console.error('Summary API error:', error);
      toast.error('Connection error');
    }
  };

  const handleReset = () => {
    setCurrentView('hero');
    setDiagnosisResult(null);
    setBudget(null);
    setFinancialSummary(null);
    setSignatureData(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {currentView !== 'client-sign' && currentView !== 'signature-confirmation' && (
        <Header />
      )}
      
      <AnimatePresence mode="wait">
        {currentView === 'hero' && (
          <motion.div key="hero" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <Hero onStart={handleStartDiagnosis} />
          </motion.div>
        )}

        {currentView === 'upload' && (
          <motion.div key="upload" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            <UploadZone onFileSelected={handleFileSelected} />
          </motion.div>
        )}

        {currentView === 'processing' && (
          <motion.div key="processing" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }}>
            <ProcessingView />
          </motion.div>
        )}

        {currentView === 'results' && diagnosisResult && (
          <motion.div key="results" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            <ResultsView 
              result={diagnosisResult} 
              onReset={handleReset}
              onGenerateBudget={handleGenerateBudget}
            />
          </motion.div>
        )}

        {currentView === 'budget' && budget && (
          <motion.div key="budget" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            <BudgetView
              budget={budget}
              onApprove={handleSendToClient}
              onEdit={() => toast('Edit mode coming soon!', { icon: '🚧' })}
              onCompleteJob={handleCompleteJob}
            />
          </motion.div>
        )}

        {currentView === 'client-sign' && budget && (
          <motion.div key="client-sign" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <ClientSignView
              budget={budget}
              onSign={handleClientSign}
              onCancel={handleReset}
            />
          </motion.div>
        )}

        {currentView === 'signature-confirmation' && signatureData && (
          <motion.div key="confirmation" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <SignatureConfirmation
              clientName={signatureData.clientName}
              budgetNumber={signatureData.budgetNumber}
              timestamp={signatureData.timestamp}
              location={signatureData.location}
              onDone={handleReset}
            />
          </motion.div>
        )}

        {currentView === 'financial-summary' && financialSummary && (
          <motion.div key="financial-summary" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            <FinancialSummaryView
              summary={financialSummary}
              onReset={handleReset}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {signatureData && (
        <ArtisanNotification
          show={showArtisanNotification}
          clientName={signatureData.clientName}
          budgetNumber={signatureData.budgetNumber}
          timestamp={signatureData.timestamp}
          onClose={() => setShowArtisanNotification(false)}
        />
      )}
    </div>
  );
}

export default AppPage;
