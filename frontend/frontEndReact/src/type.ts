export interface Encounter {
    encounter_id: number;
    patient_nbr: number;
    age: string;
    risk_level: string;
}

export interface Employee {
    id: number;
    employee_id: string;
    name: string;
    department: string | null;
    email: string | null;
    status: string | null;
}

export interface Review {
    id: number;
    employee_id: number;
    employee_name: string | null;
    period_id: number;
    period_name: string | null;
    quality_rating: number;
    delivery_rating: number;
    teamwork_rating: number;
    average_rating: number;
    comments: string | null;
    created_at: string | null;
}

export interface ReviewPeriod {
    id: number;
    name: string;
    start_date?: string;
    end_date?: string;
    status?: string;
}

export interface ReviewCreate {
    employee_id: number;
    period_id: number;
    quality_rating: number;
    delivery_rating: number;
    teamwork_rating: number;
    comments: string | null;
}

export interface ReviewFilters {
    employeeId: number | null;
    periodId: number | null;
}
