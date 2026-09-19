'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Progress } from '@/components/ui/progress'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

interface StrategyData {
  name: string
  description: string
  prime_count: number
  sum: number
  error: number
  primes: number[]
  log10_values: number[]
  cumulative_sum: number[]
}

interface DataResults {
  metadata: {
    p: number
    F1_digits: number
    F2_digits: number
    F1_first_50: string
    F1_last_20: string
    F2_first_50: string
    F2_last_20: string
    log10_F1: number
    log10_F2: number
    diff: number
    target: number
    computed_at: string
  }
  strategies: StrategyData[]
  best_strategy_index: number
}

export default function Home() {
  const [data, setData] = useState<DataResults | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedStrategy, setSelectedStrategy] = useState(0)

  useEffect(() => {
    fetch('/log10_data.json')
      .then(r => r.json())
      .then(d => {
        setData(d)
        setSelectedStrategy(d.best_strategy_index ?? 0)
        setLoading(false)
      })
      .catch(e => {
        console.error('Failed to load:', e)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-50">
        <div className="text-zinc-600 font-mono animate-pulse">در حال بارگذاری محاسبات...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-50">
        <div className="text-red-600">خطا در بارگذاری داده‌ها</div>
      </div>
    )
  }

  const meta = data.metadata
  const best = data.strategies[data.best_strategy_index]

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 via-white to-zinc-100 text-zinc-900">
      {/* Header */}
      <header className="border-b border-zinc-200 bg-white/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-zinc-900">
                فاصله‌ی log₁۰ بین دو عامل اول M(1237)
              </h1>
              <p className="text-sm text-zinc-600 mt-1" dir="rtl">
                M(1237) = 2¹²³⁷ − 1 = F₁ × F₂  —  تقریب فاصله‌ی log₁۰(F₂) − log₁₀(F₁) با جمع log₁₀ اعداد اول
              </p>
            </div>
            <Badge variant="secondary" className="self-start">
              {meta.computed_at}
            </Badge>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* The Big Numbers Section */}
        <section>
          <h2 className="text-lg font-semibold mb-3 text-zinc-800">اعداد پایه</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="border-2 border-amber-300 bg-amber-50/50">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-amber-900">F₁</CardTitle>
                  <Badge className="bg-amber-500">{meta.F1_digits} رقم</Badge>
                </div>
                <CardDescription className="text-amber-700">عامل اول شناخته‌شده — اول ✓</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 font-mono text-xs">
                <div className="break-all text-zinc-700 overflow-x-auto">
                  <span className="text-zinc-500">ابتدا:</span> {meta.F1_first_50}
                  <span className="text-zinc-400">...</span>
                </div>
                <div className="break-all text-zinc-700 overflow-x-auto">
                  <span className="text-zinc-500">انتها:</span>
                  <span className="text-zinc-400">...</span>{meta.F1_last_20}
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <span className="text-zinc-500">log₁₀(F₁) =</span>
                  <span className="text-base font-bold text-amber-900">{meta.log10_F1.toFixed(10)}</span>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2 border-rose-300 bg-rose-50/50">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-rose-900">F₂ (c303)</CardTitle>
                  <Badge className="bg-rose-500">{meta.F2_digits} رقم</Badge>
                </div>
                <CardDescription className="text-rose-700">هم‌عامل = M(1237) / F₁ — مرکب</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 font-mono text-xs">
                <div className="break-all text-zinc-700 overflow-x-auto">
                  <span className="text-zinc-500">ابتدا:</span> {meta.F2_first_50}
                  <span className="text-zinc-400">...</span>
                </div>
                <div className="break-all text-zinc-700 overflow-x-auto">
                  <span className="text-zinc-500">انتها:</span>
                  <span className="text-zinc-400">...</span>{meta.F2_last_20}
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <span className="text-zinc-500">log₁₀(F₂) =</span>
                  <span className="text-base font-bold text-rose-900">{meta.log10_F2.toFixed(10)}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* The Target: difference */}
        <Card className="border-2 border-emerald-400 bg-emerald-50/50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-emerald-900 text-xl">
                هدف: log₁₀(F₂) − log₁₀(F₁) = log₁₀(F₂/F₁)
              </CardTitle>
              <Badge className="bg-emerald-600 text-white">هدف ≈ {meta.target.toFixed(6)}</Badge>
            </div>
            <CardDescription className="text-emerald-800">
              می‌خواهیم این مقدار را به‌صورت <strong>Σ log₁₀(pᵢ)</strong> (جمع لگاریتم اعداد اول) تقریب بزنیم
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-3xl sm:text-4xl font-bold text-center text-emerald-900 py-4">
              {meta.target.toFixed(10)}
            </div>
          </CardContent>
        </Card>

        {/* Strategies Tabs */}
        <section>
          <h2 className="text-lg font-semibold mb-3 text-zinc-800">استراتژی‌های تقریب</h2>
          <Tabs defaultValue={String(selectedStrategy)} onValueChange={(v) => setSelectedStrategy(Number(v))}>
            <TabsList className="grid grid-cols-2 sm:grid-cols-4 w-full mb-4">
              {data.strategies.map((s, i) => (
                <TabsTrigger key={i} value={String(i)} className="text-xs sm:text-sm">
                  استراتژی {String.fromCharCode(65 + i)}
                </TabsTrigger>
              ))}
            </TabsList>

            {data.strategies.map((s, i) => (
              <TabsContent key={i} value={String(i)}>
                <StrategyView strategy={s} target={meta.target} />
              </TabsContent>
            ))}
          </Tabs>
        </section>

        {/* Number Line Visualization */}
        <section>
          <h2 className="text-lg font-semibold mb-3 text-zinc-800">نمودار خط‌عددی: سفر از 0 تا هدف</h2>
          <Card>
            <CardHeader>
              <CardTitle>تجمع جمع log₁۰(pᵢ) برای بهترین استراتژی</CardTitle>
              <CardDescription>
                هر نقطه نشان‌دهنده‌ی یک عدد اول است که به جمع اضافه شده. محور y = جمع تجمعی.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CumulativeChart strategy={best} target={meta.target} />
            </CardContent>
          </Card>
        </section>

        {/* Final Answer */}
        <Card className="border-2 border-zinc-900 bg-zinc-900 text-zinc-50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>نتیجه‌ی نهایی</CardTitle>
              <Badge className="bg-emerald-500 text-zinc-900">بهترین تقریب</Badge>
            </div>
            <CardDescription className="text-zinc-300">
              استراتژی: {best.name}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 font-mono">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-xs text-zinc-400">تعداد اعداد اول</div>
                <div className="text-2xl font-bold text-emerald-400">{best.prime_count}</div>
              </div>
              <div>
                <div className="text-xs text-zinc-400">جمع log₁₀(pᵢ)</div>
                <div className="text-2xl font-bold text-emerald-400">{best.sum.toFixed(10)}</div>
              </div>
              <div>
                <div className="text-xs text-zinc-400">خطا (هدف − جمع)</div>
                <div className={`text-2xl font-bold ${Math.abs(best.error) < 0.001 ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {best.error > 0 ? '+' : ''}{best.error.toExponential(3)}
                </div>
              </div>
            </div>
            <Separator className="bg-zinc-700" />
            <div className="text-sm text-zinc-300" dir="rtl">
              یعنی: <span className="font-bold text-emerald-300">F₁ × ∏ pᵢ ≈ F₂</span> با دقت نسبی{' '}
              <span className="font-bold text-emerald-300">{(Math.abs(best.error) / meta.target * 100).toExponential(3)}%</span>
            </div>
            <div className="text-sm text-zinc-300" dir="rtl">
              به عبارت دیگر، ضرب {best.prime_count} عدد اول به F₁، عددی به‌دست می‌آید که تقریباً با F₂ برابر است.
            </div>
          </CardContent>
        </Card>

        {/* Primes list */}
        <section>
          <h2 className="text-lg font-semibold mb-3 text-zinc-800">اعداد اول انتخاب‌شده (بهترین)</h2>
          <Card>
            <CardContent className="pt-6">
              <PrimesGrid primes={best.primes} log10_values={best.log10_values} />
            </CardContent>
          </Card>
        </section>

        {/* Footer */}
        <footer className="mt-12 pt-6 border-t border-zinc-200 text-center text-xs text-zinc-500">
          <p>M(1237) = 2¹²³⁷ − 1 — A136030 — محاسبه شده با Python + gmpy2 + mpmath</p>
        </footer>
      </main>
    </div>
  )
}

function StrategyView({ strategy, target }: { strategy: StrategyData; target: number }) {
  const errorAbs = Math.abs(strategy.error)
  const errorPct = (errorAbs / target) * 100
  const accuracy = 100 - errorPct
  const isBest = errorPct < 0.01

  return (
    <div className="space-y-4">
      <Card className={isBest ? "border-2 border-emerald-400" : ""}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{strategy.name}</CardTitle>
              <CardDescription>{strategy.description}</CardDescription>
            </div>
            {isBest && <Badge className="bg-emerald-500 text-white">بهترین</Badge>}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Accuracy bar */}
          <div>
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-zinc-600">دقت تقریب</span>
              <span className="font-mono font-bold text-zinc-900">
                {accuracy.toPrecision(6)}%
              </span>
            </div>
            <Progress value={Math.min(100, accuracy)} className="h-3" />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
            <Stat label="تعداد اعداد اول" value={String(strategy.prime_count)} />
            <Stat label="جمع Σlog₁₀(pᵢ)" value={strategy.sum.toFixed(8)} mono />
            <Stat label="هدف" value={target.toFixed(8)} mono />
            <Stat
              label="خطا مطلق"
              value={errorAbs.toExponential(3)}
              mono
              tone={errorAbs < 0.001 ? "good" : errorAbs < 0.1 ? "ok" : "warn"}
            />
          </div>

          {/* Mini visualization */}
          <div className="pt-2">
            <MiniBar sum={strategy.sum} target={target} />
          </div>
        </CardContent>
      </Card>

      {/* Show prime list */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">اعداد اول انتخاب‌شده</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-32 rounded border border-zinc-200 p-3">
            <div className="flex flex-wrap gap-1.5">
              {strategy.primes.map((p, idx) => (
                <Badge key={idx} variant="outline" className="font-mono text-xs">
                  {p}
                </Badge>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}

function Stat({ label, value, mono, tone }: { label: string; value: string; mono?: boolean; tone?: 'good' | 'ok' | 'warn' }) {
  const color = tone === 'good' ? 'text-emerald-600' : tone === 'ok' ? 'text-amber-600' : tone === 'warn' ? 'text-rose-600' : 'text-zinc-900'
  return (
    <div className="bg-zinc-50 rounded p-2.5 border border-zinc-200">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className={`font-bold ${mono ? 'font-mono' : ''} ${color}`}>{value}</div>
    </div>
  )
}

function MiniBar({ sum, target }: { sum: number; target: number }) {
  const pct = (sum / target) * 100
  return (
    <div className="relative h-6 bg-zinc-100 rounded overflow-hidden border border-zinc-200">
      <div
        className={`absolute inset-y-0 left-0 ${pct > 100 ? 'bg-amber-500' : 'bg-emerald-500'}`}
        style={{ width: `${Math.min(100, pct)}%` }}
      />
      <div className="absolute inset-y-0 flex items-center px-2 text-xs font-mono font-bold text-white">
        {pct.toFixed(4)}%
      </div>
      <div className="absolute inset-y-0 right-2 flex items-center text-xs font-mono text-zinc-700">
        هدف = 100%
      </div>
    </div>
  )
}

function CumulativeChart({ strategy, target }: { strategy: StrategyData; target: number }) {
  const maxVal = target * 1.05  // give a bit of headroom
  const width = 1000
  const height = 200
  const padding = { top: 10, right: 10, bottom: 20, left: 50 }
  const innerW = width - padding.left - padding.right
  const innerH = height - padding.top - padding.bottom

  const xScale = (i: number) => padding.left + (i / (strategy.prime_count - 1)) * innerW
  const yScale = (v: number) => padding.top + innerH - (v / maxVal) * innerH

  // Generate path
  let pathD = ''
  strategy.cumulative_sum.forEach((v, i) => {
    const x = xScale(i)
    const y = yScale(v)
    pathD += (i === 0 ? 'M' : 'L') + x + ',' + y + ' '
  })

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full min-w-[600px] h-auto">
        {/* Y-axis gridlines */}
        {[0, 0.25, 0.5, 0.75, 1].map(f => {
          const v = maxVal * f
          const y = yScale(v)
          return (
            <g key={f}>
              <line x1={padding.left} y1={y} x2={width - padding.right} y2={y} stroke="#e4e4e7" strokeWidth="0.5" />
              <text x={padding.left - 4} y={y + 4} textAnchor="end" className="text-[10px] fill-zinc-500 font-mono">
                {v.toFixed(1)}
              </text>
            </g>
          )
        })}
        {/* Target line */}
        <line
          x1={padding.left}
          y1={yScale(target)}
          x2={width - padding.right}
          y2={yScale(target)}
          stroke="#dc2626"
          strokeWidth="1.5"
          strokeDasharray="4 2"
        />
        <text x={width - padding.right - 4} y={yScale(target) - 4} textAnchor="end" className="text-[11px] fill-rose-600 font-bold">
          هدف = {target.toFixed(4)}
        </text>
        {/* Cumulative path */}
        <path d={pathD} fill="none" stroke="#10b981" strokeWidth="2" />
        {/* Dots at each prime */}
        {strategy.cumulative_sum.map((v, i) => (
          <TooltipProvider key={i}>
            <Tooltip>
              <TooltipTrigger asChild>
                <circle
                  cx={xScale(i)}
                  cy={yScale(v)}
                  r={2.5}
                  fill="#10b981"
                  stroke="white"
                  strokeWidth="0.5"
                  className="cursor-pointer hover:r-4"
                />
              </TooltipTrigger>
              <TooltipContent>
                <div className="font-mono text-xs">
                  <div>عدد اول #{i + 1}: p = {strategy.primes[i]}</div>
                  <div>log₁₀(p) = {strategy.log10_values[i].toFixed(6)}</div>
                  <div>جمع تجمعی = {v.toFixed(6)}</div>
                  <div>باقی‌مانده تا هدف = {(target - v).toFixed(6)}</div>
                </div>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ))}
        {/* X-axis */}
        <line x1={padding.left} y1={padding.top + innerH} x2={width - padding.right} y2={padding.top + innerH} stroke="#a1a1aa" strokeWidth="0.5" />
        {/* X-axis label */}
        <text x={width / 2} y={height - 4} textAnchor="middle" className="text-[10px] fill-zinc-500">
          شماره‌ی عدد اول (از ۱ تا {strategy.prime_count})
        </text>
      </svg>
    </div>
  )
}

function PrimesGrid({ primes, log10_values }: { primes: number[]; log10_values: number[] }) {
  const maxLog10 = Math.max(...log10_values)
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
      {primes.map((p, i) => {
        const intensity = log10_values[i] / maxLog10
        const bg = `rgba(16, 185, 129, ${0.1 + intensity * 0.4})`
        return (
          <TooltipProvider key={i}>
            <Tooltip>
              <TooltipTrigger asChild>
                <div
                  className="rounded p-2 border border-zinc-200 cursor-help text-center font-mono text-sm"
                  style={{ background: bg }}
                >
                  <div className="font-bold text-zinc-900">{p}</div>
                  <div className="text-[10px] text-zinc-600">{log10_values[i].toFixed(4)}</div>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <div className="font-mono text-xs">
                  <div>عدد اول #{i + 1}: <span className="font-bold">{p}</span></div>
                  <div>log₁₀({p}) = {log10_values[i].toFixed(10)}</div>
                </div>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )
      })}
    </div>
  )
}
