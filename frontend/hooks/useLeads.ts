import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { leadsAPI } from '@/lib/api';
import { Lead, LeadCreate, LeadUpdate } from '@/lib/types';

export const useLeads = (params?: {
  campaign_id?: string;
  status?: string;
  min_score?: number;
}) => {
  return useQuery<Lead[]>({
    queryKey: ['leads', params],
    queryFn: () => leadsAPI.getAll(params),
  });
};

export const useLead = (id: string) => {
  return useQuery<Lead>({
    queryKey: ['lead', id],
    queryFn: () => leadsAPI.getById(id),
    enabled: !!id,
  });
};

export const useCreateLead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: LeadCreate) => leadsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
};

export const useUpdateLead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: LeadUpdate }) =>
      leadsAPI.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['lead', id] });
    },
  });
};

export const useDeleteLead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => leadsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
};

export const useLeadFunnel = () => {
  return useQuery<Record<string, number>>({
    queryKey: ['leads', 'funnel'],
    queryFn: () => leadsAPI.getFunnel(),
  });
};
