'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Megaphone,
  Users,
  MessageSquare,
  UserCheck,
  Drama,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Flame,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useStore } from '@/store/useStore';
import { Progress } from '@/components/ui/progress';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Kampanyalar', href: '/campaigns', icon: Megaphone },
  { name: 'Gruplar', href: '/groups', icon: Users },
  { name: 'Mesajlar', href: '/messages', icon: MessageSquare },
  { name: 'Lead\'ler', href: '/leads', icon: UserCheck },
  { name: 'Personalar', href: '/personas', icon: Drama },
  { name: 'Analitik', href: '/analytics', icon: BarChart3 },
  { name: 'Ayarlar', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isCollapsed, toggleSidebar, warmupStatus } = useStore();

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen bg-white border-r border-gray-200 transition-all duration-300',
        isCollapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center justify-between px-4 border-b">
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-lg">TG Agent</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="ml-auto"
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || 
              (item.href !== '/' && pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                )}
              >
                <item.icon className={cn('h-5 w-5 flex-shrink-0', isActive && 'text-blue-700')} />
                {!isCollapsed && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Warm-up Status */}
        {!isCollapsed && warmupStatus && (
          <div className="p-4 border-t">
            <div className="bg-orange-50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-2">
                <Flame className="h-4 w-4 text-orange-500" />
                <span className="text-sm font-medium text-orange-700">Warm-up</span>
              </div>
              <div className="text-xs text-orange-600 mb-2">
                Aşama: {warmupStatus.current_stage}
              </div>
              <Progress value={warmupStatus.progress_percentage} className="h-2" />
              <div className="text-xs text-orange-500 mt-1">
                {warmupStatus.progress_percentage}% tamamlandı
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
