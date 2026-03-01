import { useQuery } from '@tanstack/react-query';
import { messagesAPI } from '@/lib/api';
import { Message } from '@/lib/types';

export const useMessages = (params?: {
  group_id?: string;
  campaign_id?: string;
  is_bot?: boolean;
  is_dm?: boolean;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}) => {
  return useQuery<Message[]>({
    queryKey: ['messages', params],
    queryFn: () => messagesAPI.getAll(params),
  });
};

export const useMessage = (id: string) => {
  return useQuery<Message>({
    queryKey: ['message', id],
    queryFn: () => messagesAPI.getById(id),
    enabled: !!id,
  });
};

export const useConversation = (groupId: string) => {
  return useQuery<Message[]>({
    queryKey: ['conversation', groupId],
    queryFn: () => messagesAPI.getConversation(groupId),
    enabled: !!groupId,
  });
};
