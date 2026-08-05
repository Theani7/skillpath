import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Database, Trash2, CheckCircle, AlertTriangle } from 'lucide-react';
import api from '../services/api';
import PageLoader from '../components/Skeleton';

type ToastItem = { type: 'success' | 'error'; message: string };
type CacheEntry = { content_hash: string; target_role: string; created_at: string; expires_at: number };
type ApiUsageEntry = { path: string; method: string; count: number; avg_ms: number };
type AuditLog = { id: number; admin_username: string; action: string; target_type: string; target_id: number; details?: string; created_at: string };

const AIMonitoring = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<string>('cache');
  const [cacheEntries, setCacheEntries] = useState<CacheEntry[]>([]);
  const [cacheTotal, setCacheTotal] = useState<number>(0);
  const [cachePage, setCachePage] = useState<number>(0);
  const [apiUsage, setApiUsage] = useState<ApiUsageEntry[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [auditTotal, setAuditTotal] = useState<number>(0);
  const [auditPage, setAuditPage] = useState<number>(0);
  const [toast, setToast] = useState<ToastItem | null>(null);
  const PAGE_SIZE = 20;

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3500);
  };

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [cacheRes, usageRes, auditRes] = await Promise.all([
        api.get(`/api/admin/analysis-cache?limit=${PAGE_SIZE}&offset=${cachePage * PAGE_SIZE}`),
        api.get('/api/admin/api-usage'),
        api.get(`/api/admin/audit-logs?limit=${PAGE_SIZE}&offset=${auditPage * PAGE_SIZE}`),
      ]);
      setCacheEntries(cacheRes.data.cache || []);
      setCacheTotal(cacheRes.data.total || 0);
      setApiUsage(usageRes.data.data || []);
      setAuditLogs(auditRes.data.logs || []);
      setAuditTotal(auditRes.data.total || 0);
    } catch {
      showToast('error', 'Failed to load monitoring data.');
    } finally {
      setLoading(false);
    }
  }, [cachePage, auditPage]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleDeleteCache = async (hash: string, targetRole: string) => {
    if (!confirm('Delete this cache entry?')) return;
    try {
      await api.delete(`/api/admin/analysis-cache/${encodeURIComponent(hash)}/${encodeURIComponent(targetRole)}`);
      showToast('success', 'Cache entry deleted.');
      await fetchData();
    } catch {
      showToast('error', 'Failed to delete cache entry.');
    }
  };

  if (loading) return <PageLoader />;

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '22px', fontWeight: '700', color: 'var(--color-text)', margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Database size={22} color="var(--color-primary)" /> AI Monitoring
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: '4px 0 0' }}>View analysis cache, API usage, and audit logs.</p>
      </div>

      <div style={{ display: 'flex', gap: '4px', marginBottom: '20px', padding: '4px', background: 'var(--color-bg)', borderRadius: '10px' }}>
        {[{ id: 'cache', label: 'Analysis Cache' }, { id: 'api-usage', label: 'API Usage' }, { id: 'audit', label: 'Audit Logs' }].map((tab) => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
            padding: '8px 16px', borderRadius: '8px', border: 'none', fontSize: '13px', fontWeight: '500', cursor: 'pointer',
            background: activeTab === tab.id ? 'var(--color-surface)' : 'transparent',
            color: activeTab === tab.id ? 'var(--color-text)' : 'var(--color-text-muted)',
            boxShadow: activeTab === tab.id ? 'var(--shadow-sm)' : 'none',
          }}>
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'cache' && (
        <div>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'var(--color-bg)', borderBottom: '1px solid var(--color-border)' }}>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Target Role</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Hash</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Created</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Expires</th>
                  <th style={{ width: '60px' }}></th>
                </tr>
              </thead>
              <tbody>
                {cacheEntries.length === 0 ? (
                  <tr><td colSpan={5} style={{ padding: '40px', textAlign: 'center', color: 'var(--color-text-muted)' }}>No cache entries.</td></tr>
                ) : cacheEntries.map((entry) => (
                  <tr key={`${entry.content_hash}-${entry.target_role}`} style={{ borderTop: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '12px 16px', fontSize: '13px' }}>{entry.target_role || 'General'}</td>
                    <td style={{ padding: '12px 16px', fontSize: '11px', fontFamily: 'monospace', color: 'var(--color-text-muted)' }}>{entry.content_hash?.slice(0, 12)}...</td>
                    <td style={{ padding: '12px 16px', fontSize: '13px', color: 'var(--color-text-muted)' }}>{entry.created_at}</td>
                    <td style={{ padding: '12px 16px', fontSize: '13px', color: 'var(--color-text-muted)' }}>{entry.expires_at ? new Date(entry.expires_at * 1000).toLocaleDateString() : 'Never'}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right' }}>
                      <button onClick={() => handleDeleteCache(entry.content_hash, entry.target_role)} style={{ padding: '6px', borderRadius: '6px', border: 'none', background: 'transparent', color: 'var(--color-error)', cursor: 'pointer' }}>
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {cacheTotal > PAGE_SIZE && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '16px' }}>
              <button disabled={cachePage === 0} onClick={() => setCachePage((p) => p - 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: cachePage === 0 ? 'var(--color-text-muted)' : 'var(--color-text)', cursor: cachePage === 0 ? 'default' : 'pointer', fontSize: '13px' }}>Previous</button>
              <span style={{ padding: '6px 14px', fontSize: '13px', color: 'var(--color-text-muted)' }}>Page {cachePage + 1} of {Math.ceil(cacheTotal / PAGE_SIZE)}</span>
              <button disabled={(cachePage + 1) * PAGE_SIZE >= cacheTotal} onClick={() => setCachePage((p) => p + 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: (cachePage + 1) * PAGE_SIZE >= cacheTotal ? 'var(--color-text-muted)' : 'var(--color-text)', cursor: (cachePage + 1) * PAGE_SIZE >= cacheTotal ? 'default' : 'pointer', fontSize: '13px' }}>Next</button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'api-usage' && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'var(--color-bg)', borderBottom: '1px solid var(--color-border)' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Endpoint</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Method</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Requests</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Avg Latency</th>
              </tr>
            </thead>
            <tbody>
              {apiUsage.length === 0 ? (
                <tr><td colSpan={4} style={{ padding: '40px', textAlign: 'center', color: 'var(--color-text-muted)' }}>No API usage data yet.</td></tr>
              ) : apiUsage.map((entry, idx) => (
                <tr key={idx} style={{ borderTop: '1px solid var(--color-border)' }}>
                  <td style={{ padding: '12px 16px', fontSize: '13px', fontFamily: 'monospace' }}>{entry.path}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: '600', background: entry.method === 'GET' ? 'rgba(34,197,94,0.1)' : entry.method === 'POST' ? 'rgba(59,130,246,0.1)' : 'rgba(234,179,8,0.1)', color: entry.method === 'GET' ? 'var(--color-success)' : entry.method === 'POST' ? '#3b82f6' : 'var(--color-warning)' }}>{entry.method}</span>
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '13px', textAlign: 'right', fontWeight: '500' }}>{entry.count}</td>
                  <td style={{ padding: '12px 16px', fontSize: '13px', textAlign: 'right', color: 'var(--color-text-muted)' }}>{Math.round(entry.avg_ms)} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'audit' && (
        <div>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'var(--color-bg)', borderBottom: '1px solid var(--color-border)' }}>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Admin</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Action</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Target</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Details</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Time</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.length === 0 ? (
                  <tr><td colSpan={5} style={{ padding: '40px', textAlign: 'center', color: 'var(--color-text-muted)' }}>No audit logs yet.</td></tr>
                ) : auditLogs.map((log) => (
                  <tr key={log.id} style={{ borderTop: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '12px 16px', fontSize: '13px', fontWeight: '500' }}>{log.admin_username}</td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: '600', background: log.action.includes('delete') ? 'rgba(239,68,68,0.1)' : log.action.includes('reset') ? 'rgba(234,179,8,0.1)' : 'rgba(59,130,246,0.1)', color: log.action.includes('delete') ? 'var(--color-error)' : log.action.includes('reset') ? 'var(--color-warning)' : '#3b82f6' }}>{log.action}</span>
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '13px', color: 'var(--color-text-muted)' }}>{log.target_type} #{log.target_id}</td>
                    <td style={{ padding: '12px 16px', fontSize: '12px', color: 'var(--color-text-muted)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{log.details || '-'}</td>
                    <td style={{ padding: '12px 16px', fontSize: '12px', color: 'var(--color-text-muted)' }}>{log.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {auditTotal > PAGE_SIZE && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '16px' }}>
              <button disabled={auditPage === 0} onClick={() => setAuditPage((p) => p - 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: auditPage === 0 ? 'var(--color-text-muted)' : 'var(--color-text)', cursor: auditPage === 0 ? 'default' : 'pointer', fontSize: '13px' }}>Previous</button>
              <span style={{ padding: '6px 14px', fontSize: '13px', color: 'var(--color-text-muted)' }}>Page {auditPage + 1} of {Math.ceil(auditTotal / PAGE_SIZE)}</span>
              <button disabled={(auditPage + 1) * PAGE_SIZE >= auditTotal} onClick={() => setAuditPage((p) => p + 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: (auditPage + 1) * PAGE_SIZE >= auditTotal ? 'var(--color-text-muted)' : 'var(--color-text)', cursor: (auditPage + 1) * PAGE_SIZE >= auditTotal ? 'default' : 'pointer', fontSize: '13px' }}>Next</button>
            </div>
          )}
        </div>
      )}

      <AnimatePresence>
        {toast && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }} style={{ position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)', background: toast.type === 'success' ? 'var(--color-success)' : 'var(--color-error)', color: 'white', padding: '12px 20px', borderRadius: '10px', fontSize: '14px', fontWeight: '600', zIndex: 50, display: 'flex', alignItems: 'center', gap: '8px' }}>
            {toast.type === 'success' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
            {toast.message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AIMonitoring;
