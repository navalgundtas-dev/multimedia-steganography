import React, { useState } from 'react';
import { AlertTriangle, Shield, Info, Share2, Lock } from 'lucide-react';

const tips = [
  {
    icon: AlertTriangle,
    title: 'Compression Awareness',
    body: 'Avoid platforms that recompress media (e.g., social networks) because lossy codecs destroy LSB payloads. Share files as attachments or via lossless storage services.',
  },
  {
    icon: Shield,
    title: 'Preserve Originals',
    body: 'Never re-save or edit the stego file after embedding. Even minor edits or filters can scramble the embedded bits.',
  },
  {
    icon: Share2,
    title: 'Exchange Checklist',
    body: 'Agree on password, media format, and transfer method ahead of time. Verify file hashes before and after sending when possible.',
  },
  {
    icon: Lock,
    title: 'Password Hygiene',
    body: 'Use strong, unique passwords for AES encryption. Share them through a separate secure channel, not with the media itself.',
  },
  {
    icon: Info,
    title: 'Know the Limits',
    body: 'LSB works best on uncompressed formats (BMP, PNG, WAV). Capacity is finite; overfilling leads to corruption or easy detection.',
  },
];

const LsbGuide = () => {
  const [expanded, setExpanded] = useState(false);

  return (
    <section className="mt-12">
      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
        <button
          onClick={() => setExpanded((prev) => !prev)}
          className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div>
            <p className="text-sm font-semibold text-primary-600 tracking-wide uppercase">LSB Safety Brief</p>
            <h3 className="text-lg font-bold text-gray-900">
              Best practices for sharing stego media without losing hidden data
            </h3>
          </div>
          <span className="text-sm font-medium text-primary-600">
            {expanded ? 'Hide details' : 'Show details'}
          </span>
        </button>

        {expanded && (
          <div className="px-6 pb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {tips.map((tip) => {
                const Icon = tip.icon;
                return (
                  <div key={tip.title} className="p-4 bg-primary-50 border border-primary-100 rounded-xl">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-white rounded-full shadow-sm">
                        <Icon className="w-5 h-5 text-primary-600" />
                      </div>
                      <h4 className="text-sm font-semibold text-gray-900">{tip.title}</h4>
                    </div>
                    <p className="mt-2 text-sm text-gray-700 leading-relaxed">{tip.body}</p>
                  </div>
                );
              })}
            </div>
            <p className="mt-6 text-xs text-gray-500">
              Reminder: This app uses LSB variants with AES encryption, but no steganography survives aggressive
              recompression or format conversions. When in doubt, transmit losslessly.
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default LsbGuide;













