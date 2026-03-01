import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { personasAPI } from '@/lib/api';
import { Persona, PersonaCreate, PersonaUpdate } from '@/lib/types';

export const usePersonas = (activeOnly?: boolean) => {
  return useQuery<Persona[]>({
    queryKey: ['personas', activeOnly],
    queryFn: () => personasAPI.getAll(activeOnly),
  });
};

export const usePersona = (id: string) => {
  return useQuery<Persona>({
    queryKey: ['persona', id],
    queryFn: () => personasAPI.getById(id),
    enabled: !!id,
  });
};

export const useCreatePersona = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PersonaCreate) => personasAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['personas'] });
    },
  });
};

export const useUpdatePersona = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PersonaUpdate }) =>
      personasAPI.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['personas'] });
      queryClient.invalidateQueries({ queryKey: ['persona', id] });
    },
  });
};

export const useDeletePersona = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => personasAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['personas'] });
    },
  });
};

export const usePreviewPersona = () => {
  return useMutation({
    mutationFn: ({ id, sampleMessage }: { id: string; sampleMessage?: string }) =>
      personasAPI.preview(id, sampleMessage),
  });
};
