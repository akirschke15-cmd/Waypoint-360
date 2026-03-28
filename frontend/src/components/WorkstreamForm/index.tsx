import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';

export default function WorkstreamForm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    short_name: '',
    purpose: '',
    scope_in: '',
    scope_out: '',
    status: 'not_started',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // POST to backend when create endpoint exists
    console.log('Form submitted:', formData);
    navigate('/');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <button onClick={() => navigate('/')} className="flex items-center gap-1 text-sm text-neutral-500 hover:text-swa-blue transition-colors mb-3">
          <ArrowLeft size={14} /> Back
        </button>
        <h1 className="text-2xl font-bold text-neutral-100">New Workstream</h1>
        <p className="text-sm text-neutral-400 mt-1">Add a workstream to the Waypoint program</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="bg-neutral-800 border border-neutral-700 rounded-xl p-6 space-y-4">
          <div>
            <label className="block text-xs text-neutral-400 uppercase tracking-wider mb-1.5">Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-neutral-900 border border-neutral-600 rounded-lg px-4 py-2.5 text-sm text-neutral-200 focus:outline-none focus:border-swa-blue transition-colors"
              placeholder="e.g., Customer Experience"
              required
            />
          </div>
          <div>
            <label className="block text-xs text-neutral-400 uppercase tracking-wider mb-1.5">Short Name</label>
            <input
              type="text"
              value={formData.short_name}
              onChange={(e) => setFormData({ ...formData, short_name: e.target.value })}
              className="w-full bg-neutral-900 border border-neutral-600 rounded-lg px-4 py-2.5 text-sm text-neutral-200 focus:outline-none focus:border-swa-blue transition-colors"
              placeholder="e.g., CX"
              required
            />
          </div>
          <div>
            <label className="block text-xs text-neutral-400 uppercase tracking-wider mb-1.5">Purpose</label>
            <textarea
              value={formData.purpose}
              onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
              rows={3}
              className="w-full bg-neutral-900 border border-neutral-600 rounded-lg px-4 py-2.5 text-sm text-neutral-200 focus:outline-none focus:border-swa-blue transition-colors resize-none"
              placeholder="What is this workstream responsible for?"
              required
            />
          </div>
          <div>
            <label className="block text-xs text-neutral-400 uppercase tracking-wider mb-1.5">Scope In (one per line)</label>
            <textarea
              value={formData.scope_in}
              onChange={(e) => setFormData({ ...formData, scope_in: e.target.value })}
              rows={3}
              className="w-full bg-neutral-900 border border-neutral-600 rounded-lg px-4 py-2.5 text-sm text-neutral-200 focus:outline-none focus:border-swa-blue transition-colors resize-none"
              placeholder="Items explicitly in scope"
            />
          </div>
          <div>
            <label className="block text-xs text-neutral-400 uppercase tracking-wider mb-1.5">Scope Out (one per line)</label>
            <textarea
              value={formData.scope_out}
              onChange={(e) => setFormData({ ...formData, scope_out: e.target.value })}
              rows={3}
              className="w-full bg-neutral-900 border border-neutral-600 rounded-lg px-4 py-2.5 text-sm text-neutral-200 focus:outline-none focus:border-swa-blue transition-colors resize-none"
              placeholder="Items explicitly excluded"
            />
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-4 py-2.5 bg-neutral-700 text-neutral-300 rounded-lg text-sm hover:bg-neutral-600 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="flex items-center gap-2 px-5 py-2.5 bg-swa-blue text-white rounded-lg text-sm hover:bg-swa-blue/80 transition-colors"
          >
            <Save size={16} />
            Create Workstream
          </button>
        </div>
      </form>
    </div>
  );
}
