export interface DiagnosisResult {
  execution_summary: {
    total_duration_ms: number;
    total_cost_usd: number;
    successful_tasks: number;
    total_tasks: number;
  };
  consolidated_response: {
    diagnosis: string;
    severity: string;
    procedure_summary: string;
    key_tools: string[];
    part_number: string | null;
    manual_reference: string | null;
    safety_warnings: string[];
    estimated_cost: string;
    estimated_time: string;
  };
  agent_results: {
    [key: string]: any;
  };
  voice_response?: {
    data?: {
      spoken_response?: string;
      estimated_duration_seconds?: number;
    };
  };
  steward_analysis?: Budget | null;
}

export interface BudgetMetadata {
  budget_number: string;
  issue_date: string;
  valid_until: string;
  job_title: string;
}

export interface ClientInfo {
  name: string;
  address: string | null;
  contact: string | null;
}

export interface JobDescription {
  summary: string;
  scope: string[];
  exclusions: string[];
  estimated_duration: string;
}

export interface PartItem {
  item: string;
  quantity: number;
  unit_price: number;
  total: number;
}

export interface LaborInfo {
  estimated_hours: number;
  hourly_rate: number;
  total: number;
}

export interface CostBreakdown {
  parts: PartItem[];
  parts_subtotal: number;
  labor: LaborInfo;
  consumables: number;
  subtotal: number;
  margin_percentage: number;
  margin_amount: number;
  tax_percentage: number;
  tax_amount: number;
  total: number;
  total_rounded: number;
}

export interface PaymentTerms {
  deposit_percentage: number;
  deposit_amount: number;
  balance_due: string;
  accepted_methods: string[];
  late_fee_policy: string;
}

export interface Warranty {
  parts_warranty: string;
  labor_warranty: string;
  void_conditions: string[];
}

export interface FinancialHealth {
  effective_hourly_rate: number;
  profit_margin_percentage: number;
  risk_level: string;
  recommendation: string;
}

export interface Budget {
  budget_mode: string;
  budget_metadata: BudgetMetadata;
  client_info: ClientInfo;
  job_description: JobDescription;
  cost_breakdown: CostBreakdown;
  payment_terms: PaymentTerms;
  warranty: Warranty;
  financial_health: FinancialHealth;
  client_friendly_total: string;
}

export interface Profitability {
  gross_revenue: number;
  direct_costs: number;
  gross_profit: number;
  net_margin_percentage: number;
  effective_hourly_rate: number;
  profitability_grade: string;
}

export interface PerformanceMetrics {
  time_efficiency: string;
  cost_efficiency: string;
  margin_vs_target: string;
  overall_score: number;
  score_label: string;
}

export interface Insights {
  what_went_well: string[];
  what_to_improve: string[];
  pricing_recommendation: string;
  red_flags: string[];
}

export interface ChartData {
  cost_breakdown: {
    parts: number;
    labor: number;
    margin: number;
    taxes: number;
  };
  budget_vs_actual: {
    budgeted_parts: number;
    actual_parts: number;
    budgeted_labor: number;
    actual_labor: number;
    budgeted_total: number;
    actual_total: number;
  };
}

export interface FinancialSummary {
  summary_mode: string;
  job_info: {
    job_id: string;
    client_name: string;
    job_title: string;
    date: string;
    duration_actual: string;
    duration_estimated: string;
  };
  comparison: {
    budgeted_total: number;
    actual_total: number;
    variance: number;
    variance_percentage: number;
    variance_reason: string;
  };
  cost_analysis: {
    parts_budgeted: number;
    parts_actual: number;
    parts_variance: number;
    labor_hours_budgeted: number;
    labor_hours_actual: number;
    labor_hours_variance: number;
    extra_costs: Array<{
      item: string;
      amount: number;
      reason: string;
    }>;
  };
  profitability: Profitability;
  performance_metrics: PerformanceMetrics;
  insights: Insights;
  chart_data: ChartData;
  celebration_message: string;
}

export interface UploadState {
  file: File | null;
  preview: string | null;
  description: string;
}

// ─────────────────────────────────────────────
// ARTISAN DASHBOARD TYPES
// ─────────────────────────────────────────────

export interface ArtisanJob {
  job_id: string;
  client_name: string;
  client_phone: string;
  client_email: string;
  client_address: string;
  date: string;
  diagnosis: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed';
  trade: string;
  final_cost: number;
  parts_cost: number;
  labor_cost: number;
  profit: number;
  grade: string;
  duration_minutes: number;
  hourly_rate?: number;
  is_demo?: boolean;
}

export interface RevenueTrend {
  month: string;
  revenue: number;
}

export interface StatusDistribution {
  completed: number;
  'in-progress': number;
  pending: number;
}

export interface DashboardStats {
  total_jobs: number;
  total_clients: number;
  completed_jobs: number;
  in_progress_jobs: number;
  pending_jobs: number;
  total_revenue: number;
  total_profit: number;
  total_parts_cost: number;
  total_labor_cost: number;
  average_profit: number;
  average_grade: string;
  average_duration_minutes: number;
  status_distribution: StatusDistribution;
  revenue_trend: RevenueTrend[];
}

export interface StewardSuggestionItem {
  category: string;
  title: string;
  suggestion: string;
  reason: string;
  action: string;
  potential_impact: string;
}

export interface StewardSuggestion {
  business_health: string;
  focus_priority: string;
  suggestions: StewardSuggestionItem[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}
