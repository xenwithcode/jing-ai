import axios from 'axios';
import type { Budget, FinancialSummary, DashboardStats, ArtisanJob, StewardSuggestion } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ═══════════════════════════════════════════════════════════════
// DIAGNOSE ENDPOINTS
// ═══════════════════════════════════════════════════════════════

export async function diagnoseProblem(
  image: File,
  voiceText: string
): Promise<any> {
  const formData = new FormData();
  formData.append('image', image);
  formData.append('voice_text', voiceText);

  const response = await api.post('/diagnose', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

export async function diagnoseSimple(
  image: File | null,
  voiceText: string
): Promise<any> {
  const formData = new FormData();
  if (image) {
    formData.append('image', image);
  }
  formData.append('voice_text', voiceText);

  const response = await api.post('/diagnose/simple', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

// ═══════════════════════════════════════════════════════════════
// BUDGET ENDPOINTS
// ═══════════════════════════════════════════════════════════════

export async function generateBudget(data: {
  diagnosis: string;
  parts?: Array<{
    item: string;
    quantity: number;
    unit_price: number;
    total?: number;
  }>;
  tools?: string[];
  estimated_hours?: number;
  trade?: string;
  client_name?: string;
  urgency?: string;
}): Promise<{ success: boolean; budget: Budget; error?: string }> {
  const response = await api.post('/budget/generate', data);
  return response.data;
}

export async function generateFinancialSummary(data: {
  budget: any;
  actual_parts_cost: number;
  actual_hours: number;
  amount_charged: number;
  client_name: string;
  job_title?: string;
  extra_costs?: Array<{
    item: string;
    amount: number;
    reason: string;
  }>;
}): Promise<{ success: boolean; summary: FinancialSummary; error?: string }> {
  const response = await api.post('/budget/summary', data);
  return response.data;
}

// ═══════════════════════════════════════════════════════════════
// HEALTH ENDPOINTS
// ═══════════════════════════════════════════════════════════════

export async function healthCheck(): Promise<any> {
  const response = await api.get('/health');
  return response.data;
}

// ═══════════════════════════════════════════════════════════════
// ARTISAN DASHBOARD ENDPOINTS
// ═══════════════════════════════════════════════════════════════

export async function getDashboardStats(trade?: string): Promise<{ success: boolean; data: DashboardStats }> {
  const params = trade ? { trade } : {};
  const response = await api.get('/artisan/dashboard', { params });
  return response.data;
}

export async function getArtisanJobs(trade?: string, status?: string): Promise<{ success: boolean; data: { jobs: ArtisanJob[]; total: number; stats: DashboardStats } }> {
  const params: Record<string, string> = {};
  if (trade) params.trade = trade;
  if (status) params.status = status;
  const response = await api.get('/artisan/jobs', { params });
  return response.data;
}

export async function seedDemoData(trade: string): Promise<{ success: boolean; message: string; seeded: number }> {
  const response = await api.post('/artisan/seed-demo', { trade });
  return response.data;
}

export async function getStewardSuggestion(trade?: string): Promise<{ success: boolean; data: StewardSuggestion }> {
  const params = trade ? { trade } : {};
  const response = await api.get('/artisan/steward-suggestion', { params });
  return response.data;
}

export async function updateJobStatus(jobId: string, status: string): Promise<{ success: boolean; data: ArtisanJob }> {
  const response = await api.patch(`/artisan/jobs/${jobId}/status`, { status });
  return response.data;
}

export default api;
