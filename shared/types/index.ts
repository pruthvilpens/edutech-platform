// User Types
export enum UserRole {
  ADMIN = 'admin',
  INSTRUCTOR = 'instructor',
  STUDENT = 'student',
}

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  isActive: boolean;
  emailVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

// Document Types
export enum DocumentStatus {
  UPLOADED = 'uploaded',
  PROCESSING = 'processing',
  PROCESSED = 'processed',
  FAILED = 'failed',
}

export interface Document {
  id: string;
  uploadedBy: string;
  originalFilename: string;
  filePath: string;
  fileSize: number;
  mimeType: string;
  status: DocumentStatus;
  metadata: Record<string, any>;
  createdAt: string;
  processedAt?: string;
}

// Question Types
export interface Question {
  id: string;
  documentId?: string;
  createdBy: string;
  questionText: string;
  questionType: string;
  options: string[];
  correctAnswer: string;
  explanation?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

// Test Types
export enum TestStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
}

export interface Test {
  id: string;
  createdBy: string;
  title: string;
  description?: string;
  status: TestStatus;
  durationMinutes?: number;
  totalMarks: number;
  passingMarks: number;
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  publishedAt?: string;
}

// Result Types
export interface Result {
  id: string;
  testId: string;
  userId: string;
  score: number;
  totalMarks: number;
  percentage: number;
  timeTakenSeconds: number;
  answers: Record<string, any>;
  submittedAt: string;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
    