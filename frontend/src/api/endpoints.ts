export const ENDPOINTS = {
  // auth
  login: '/auth/login',
  register: '/auth/register',
  refresh: '/auth/refresh',
  me: '/auth/me',
  resetPassword: '/auth/reset-password',

  // documents
  documents: '/documents',
  document: (id: number) => `/documents/${id}`,
  uploadDocument: '/documents/upload',

  // analysis
  analysis: '/analysis',
  analysisByDocument: (documentId: number) => `/analysis/by-document/${documentId}`,
  analysisDetail: (id: number) => `/analysis/${id}`,
  analysisSummary: '/analysis/summary',
  analysisReport: (id: number) => `/analysis/${id}/report`,

  // reports
  reports: '/reports',

  // chat
  chat: '/chat',
  chatCapabilities: '/chat/capabilities',
  chatSessions: '/chat/sessions',
  chatSession: (id: string) => `/chat/sessions/${id}`,
  chatArtifact: (fileId: string) => `/chat/artifacts/${encodeURIComponent(fileId)}`,
} as const
