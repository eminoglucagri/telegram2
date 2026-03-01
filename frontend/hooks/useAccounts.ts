import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accountsAPI } from '@/lib/api';
import { Account, InitiateLoginRequest, VerifyCodeRequest, AccountStatusResponse } from '@/lib/types';

export const useAccounts = () => {
  return useQuery<Account[]>({
    queryKey: ['accounts'],
    queryFn: () => accountsAPI.getAll(),
  });
};

export const useAccount = (id: number) => {
  return useQuery<Account>({
    queryKey: ['account', id],
    queryFn: () => accountsAPI.getById(id),
    enabled: !!id,
  });
};

export const useAccountStatus = (id: number) => {
  return useQuery<AccountStatusResponse>({
    queryKey: ['accountStatus', id],
    queryFn: () => accountsAPI.getStatus(id),
    enabled: !!id,
    refetchInterval: 60000, // Refresh every minute
  });
};

export const useInitiateLogin = () => {
  return useMutation({
    mutationFn: (data: InitiateLoginRequest) => accountsAPI.initiateLogin(data),
  });
};

export const useVerifyCode = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: VerifyCodeRequest) => accountsAPI.verifyCode(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });
};

export const useDeleteAccount = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => accountsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });
};

export const useCheckAccountStatus = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => accountsAPI.getStatus(id),
    onSuccess: (data, id) => {
      queryClient.invalidateQueries({ queryKey: ['accountStatus', id] });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });
};
