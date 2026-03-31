"use client";

import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/feedback/empty-state";

const metricCards = [
  { title: "Total Contacts", key: "contacts" },
  { title: "Open Deals", key: "deals" },
  { title: "Revenue (Won)", key: "revenue" },
  { title: "Pending Tasks", key: "tasks" },
];

export default function DashboardPage() {
  // TODO: wire up data fetching when dashboard API is available
  function handleRefresh() {}

  return (
    <AppShell>
      <PageHeader
        title="Dashboard"
        actions={
          <Button variant="secondary" onClick={handleRefresh}>
            Refresh
          </Button>
        }
      />
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {metricCards.map((card) => (
          <Card key={card.key} header={<h3 className="text-sm font-medium text-neutral-500">{card.title}</h3>}>
            <EmptyState title="No data yet" description="Data will appear here once available." />
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
