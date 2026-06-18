import React from 'react';
import { Layers, Shield, Zap, Waves } from 'lucide-react';

const highlights = [
  {
    icon: Layers,
    title: 'Multi-Modal Engine',
    desc: 'Images, audio, video, text and voice stego workflows in one place.',
  },
  {
    icon: Shield,
    title: 'End-to-End Encryption',
    desc: 'AES-protected payloads with password-based key derivation.',
  },
  {
    icon: Waves,
    title: 'Adaptive Algorithms',
    desc: 'Voice-aware embedding plus LSB strategies tuned per media type.',
  },
];

const stats = [
  { label: 'Media Types', value: '5+' },
  { label: 'Max File Size', value: '100 MB' },
  { label: 'Encryption', value: 'AES-256' },
];

const HeroBanner = () => {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/20 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 px-6 py-10 shadow-2xl shadow-slate-900/20 mb-10 text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.08),_transparent_45%)] pointer-events-none" />

      <div className="relative flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
        <div className="flex-1 space-y-4">
          <p className="inline-flex items-center space-x-2 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-teal-200">
            <Zap className="w-3.5 h-3.5" />
            <span>Steganography Studio</span>
          </p>
          <h1 className="text-3xl sm:text-4xl font-bold leading-tight text-white">
            Hide secrets inside everyday media with <span className="text-teal-300">pixel-perfect</span> control.
          </h1>
          <p className="text-slate-200 text-base max-w-2xl">
            Upload, encrypt, and transmit hidden payloads while preserving perceptual quality. Switch between image, audio,
            video, text, and voice channels without leaving the dashboard.
          </p>
        </div>

        <div className="flex-1 grid grid-cols-3 gap-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="rounded-2xl bg-white/10 backdrop-blur-lg border border-white/20 px-4 py-5 text-center shadow-lg"
            >
              <p className="text-2xl font-bold text-white">{stat.value}</p>
              <p className="text-xs uppercase tracking-wide text-slate-200">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="relative mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {highlights.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.title}
              className="group rounded-2xl border border-white/15 bg-white/5 p-5 backdrop-blur-lg transition hover:-translate-y-1 hover:border-teal-200/60"
            >
              <div className="mb-3 inline-flex items-center justify-center rounded-full bg-white/10 p-3 text-teal-200">
                <Icon className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-white">{item.title}</h3>
              <p className="mt-1 text-sm text-slate-200">{item.desc}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default HeroBanner;













