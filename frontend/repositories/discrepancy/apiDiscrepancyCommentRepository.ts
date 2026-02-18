import api from '@/services/api.service';

export const getDiscrepancyComments = (discrepancyId: number) => {
  return api.get(`/discrepancies/${discrepancyId}/comments`);
};

export const postDiscrepancyComment = (discrepancyId: number, content: string) => {
  return api.post(`/discrepancies/${discrepancyId}/comments`, { content });
}; 