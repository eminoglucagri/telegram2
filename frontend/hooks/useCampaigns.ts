import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { campaignsAPI } from '@/lib/api';
import { Campaign, CampaignCreate, CampaignUpdate } from '@/lib/types';

export const useCampaigns = (status?: string) => {
  return useQuery<Campaign[]>({
    queryKey: ['campaigns', status],
    queryFn: () => campaignsAPI.getAll(status),
  });
};

export const useCampaign = (id: string) => {
  return useQuery<Campaign>({
    queryKey: ['campaign', id],
    queryFn: () => campaignsAPI.getById(id),
    enabled: !!id,
  });
};

export const useCreateCampaign = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CampaignCreate) => campaignsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
    },
  });
};

export const useUpdateCampaign = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CampaignUpdate }) =>
      campaignsAPI.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['campaign', id] });
    },
  });
};

export const useDeleteCampaign = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => campaignsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
    },
  });
};

export const useActivateCampaign = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => campaignsAPI.activate(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['campaign', id] });
    },
  });
};

export const usePauseCampaign = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => campaignsAPI.pause(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['campaign', id] });
    },
  });
};
