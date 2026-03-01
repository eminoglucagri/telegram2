import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Campaign, Group, Lead, Persona, WarmUpStatus } from '@/lib/types';

interface SidebarState {
  isCollapsed: boolean;
  toggleSidebar: () => void;
  setCollapsed: (collapsed: boolean) => void;
}

interface FilterState {
  campaignFilter: string;
  groupFilter: string;
  leadFilter: string;
  dateRange: { start: string | null; end: string | null };
  setCampaignFilter: (filter: string) => void;
  setGroupFilter: (filter: string) => void;
  setLeadFilter: (filter: string) => void;
  setDateRange: (range: { start: string | null; end: string | null }) => void;
  clearFilters: () => void;
}

interface CacheState {
  campaigns: Campaign[];
  groups: Group[];
  leads: Lead[];
  personas: Persona[];
  warmupStatus: WarmUpStatus | null;
  setCampaigns: (campaigns: Campaign[]) => void;
  setGroups: (groups: Group[]) => void;
  setLeads: (leads: Lead[]) => void;
  setPersonas: (personas: Persona[]) => void;
  setWarmupStatus: (status: WarmUpStatus | null) => void;
  addCampaign: (campaign: Campaign) => void;
  updateCampaign: (id: string, campaign: Partial<Campaign>) => void;
  removeCampaign: (id: string) => void;
  addGroup: (group: Group) => void;
  updateGroup: (id: string, group: Partial<Group>) => void;
  removeGroup: (id: string) => void;
  addLead: (lead: Lead) => void;
  updateLead: (id: string, lead: Partial<Lead>) => void;
  removeLead: (id: string) => void;
}

interface NotificationState {
  notifications: Array<{ id: string; type: 'success' | 'error' | 'info' | 'warning'; message: string }>;
  addNotification: (type: 'success' | 'error' | 'info' | 'warning', message: string) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

type AppState = SidebarState & FilterState & CacheState & NotificationState;

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // Sidebar State
      isCollapsed: false,
      toggleSidebar: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
      setCollapsed: (collapsed) => set({ isCollapsed: collapsed }),

      // Filter State
      campaignFilter: '',
      groupFilter: '',
      leadFilter: '',
      dateRange: { start: null, end: null },
      setCampaignFilter: (filter) => set({ campaignFilter: filter }),
      setGroupFilter: (filter) => set({ groupFilter: filter }),
      setLeadFilter: (filter) => set({ leadFilter: filter }),
      setDateRange: (range) => set({ dateRange: range }),
      clearFilters: () => set({
        campaignFilter: '',
        groupFilter: '',
        leadFilter: '',
        dateRange: { start: null, end: null },
      }),

      // Cache State
      campaigns: [],
      groups: [],
      leads: [],
      personas: [],
      warmupStatus: null,
      setCampaigns: (campaigns) => set({ campaigns }),
      setGroups: (groups) => set({ groups }),
      setLeads: (leads) => set({ leads }),
      setPersonas: (personas) => set({ personas }),
      setWarmupStatus: (status) => set({ warmupStatus: status }),
      addCampaign: (campaign) => set((state) => ({ campaigns: [...state.campaigns, campaign] })),
      updateCampaign: (id, campaign) => set((state) => ({
        campaigns: state.campaigns.map((c) => (c.id === id ? { ...c, ...campaign } : c)),
      })),
      removeCampaign: (id) => set((state) => ({
        campaigns: state.campaigns.filter((c) => c.id !== id),
      })),
      addGroup: (group) => set((state) => ({ groups: [...state.groups, group] })),
      updateGroup: (id, group) => set((state) => ({
        groups: state.groups.map((g) => (g.id === id ? { ...g, ...group } : g)),
      })),
      removeGroup: (id) => set((state) => ({
        groups: state.groups.filter((g) => g.id !== id),
      })),
      addLead: (lead) => set((state) => ({ leads: [...state.leads, lead] })),
      updateLead: (id, lead) => set((state) => ({
        leads: state.leads.map((l) => (l.id === id ? { ...l, ...lead } : l)),
      })),
      removeLead: (id) => set((state) => ({
        leads: state.leads.filter((l) => l.id !== id),
      })),

      // Notification State
      notifications: [],
      addNotification: (type, message) => set((state) => ({
        notifications: [
          ...state.notifications,
          { id: Date.now().toString(), type, message },
        ],
      })),
      removeNotification: (id) => set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== id),
      })),
      clearNotifications: () => set({ notifications: [] }),
    }),
    {
      name: 'telegram-agent-storage',
      partialize: (state) => ({
        isCollapsed: state.isCollapsed,
        campaignFilter: state.campaignFilter,
        groupFilter: state.groupFilter,
        leadFilter: state.leadFilter,
      }),
    }
  )
);

export default useStore;
