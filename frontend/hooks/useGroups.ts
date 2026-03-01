import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { groupsAPI } from '@/lib/api';
import { Group, GroupCreate, GroupUpdate } from '@/lib/types';

export const useGroups = (status?: string) => {
  return useQuery<Group[]>({
    queryKey: ['groups', status],
    queryFn: () => groupsAPI.getAll(status),
  });
};

export const useGroup = (id: string) => {
  return useQuery<Group>({
    queryKey: ['group', id],
    queryFn: () => groupsAPI.getById(id),
    enabled: !!id,
  });
};

export const useAddGroup = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: GroupCreate) => groupsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] });
    },
  });
};

export const useUpdateGroup = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: GroupUpdate }) =>
      groupsAPI.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['groups'] });
      queryClient.invalidateQueries({ queryKey: ['group', id] });
    },
  });
};

export const useLeaveGroup = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => groupsAPI.leave(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] });
    },
  });
};

export const useAssignGroupToCampaign = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, campaignId }: { id: string; campaignId: string }) =>
      groupsAPI.assignToCampaign(id, campaignId),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['groups'] });
      queryClient.invalidateQueries({ queryKey: ['group', id] });
    },
  });
};
