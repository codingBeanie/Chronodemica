<script lang="ts">
  import { browser } from '$app/environment';
  import { getDistanceScoring, type DistanceScoring } from '../../lib/api/data_services/simulation';
  import type { PopPeriod } from '../../lib/api/core';

  interface ThemeColors {
    accent: string;
    dark: string;
    darkAlt: string;
    light: string;
    lightAlt: string;
    success: string;
    failure: string;
  }

  interface PlotTrace {
    x: number[];
    y: number[];
    name: string;
    type: string;
    mode: string;
    line: {
      color: string;
      width: number;
    };
  }

  const { popPeriod, refreshTrigger } = $props<{ popPeriod: PopPeriod | null; refreshTrigger?: number }>();

  // Central configuration
  const PLOT_CONFIG = {
    AXIS_RANGE: {
      x: [0, 100] as const,
      y: [0, 100] as const
    },
    MARGIN: { t: 10, l: 50, r: 20, b: 50 } as const,
    FONT_SIZE: { default: 12, title: 14 } as const,
    LEGEND: {
      orientation: 'h' as const,
      x: 0.5,
      xanchor: 'center' as const,
      y: 1.02,
      yanchor: 'bottom' as const
    },
    LINE: {
      width: 3
    }
  };

  let plotDiv: HTMLDivElement;
  let loading = $state(false);
  let error = $state<string | null>(null);
  let Plotly: any = null;

  function getThemeColors(): ThemeColors {
    const root = document.documentElement;
    const computedStyle = getComputedStyle(root);
    
    return {
      accent: computedStyle.getPropertyValue('--accent').trim(),
      dark: computedStyle.getPropertyValue('--dark').trim(),
      darkAlt: computedStyle.getPropertyValue('--dark-alt').trim(),
      light: computedStyle.getPropertyValue('--light').trim(),
      lightAlt: computedStyle.getPropertyValue('--light-alt').trim(),
      success: computedStyle.getPropertyValue('--success').trim(),
      failure: computedStyle.getPropertyValue('--failure').trim()
    };
  }

  async function initPlotly() {
    if (!Plotly && browser) {
      Plotly = await import('plotly.js-dist-min');
    }
    return Plotly;
  }

  function createTrace(scoringData: DistanceScoring[], colors: ThemeColors): PlotTrace {
    const x = scoringData.map(d => d.distance);
    const y = scoringData.map(d => d.score);
    
    return {
      x,
      y,
      name: 'Scoring Curve',
      type: 'scatter',
      mode: 'lines',
      line: {
        color: colors.accent,
        width: PLOT_CONFIG.LINE.width
      }
    };
  }

  function createLayout(colors: ThemeColors) {
    return {
      xaxis: {
        title: {
          text: 'Political Distance',
          font: { color: colors.dark, family: 'Noto Sans, sans-serif' }
        },
        range: PLOT_CONFIG.AXIS_RANGE.x,
        showticklabels: true,
        zeroline: true,
        color: colors.dark,
        ticklen: 5,
        tickpad: 10
      },
      yaxis: {
        title: {
          text: 'Score',
          font: { color: colors.dark, family: 'Noto Sans, sans-serif' }
        },
        range: PLOT_CONFIG.AXIS_RANGE.y,
        showticklabels: true,
        zeroline: true,
        color: colors.dark,
        ticklen: 5,
        tickpad: 10
      },
      showlegend: false,
      margin: PLOT_CONFIG.MARGIN,
      paper_bgcolor: colors.light,
      plot_bgcolor: colors.light,
      font: { color: colors.dark, size: PLOT_CONFIG.FONT_SIZE.default, family: 'Noto Sans, sans-serif' }
    };
  }

  async function fetchData(popPeriod: PopPeriod): Promise<DistanceScoring[]> {
    try {
      const result = await getDistanceScoring(popPeriod);
      if (result.success && result.data) {
        return result.data;
      } else {
        throw new Error(result.error || 'Failed to fetch scoring data');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch scoring data';
      throw new Error(errorMessage);
    }
  }

  function hasData(scoringData: DistanceScoring[]): boolean {
    return scoringData.length > 0;
  }

  async function renderPlot() {
    if (!browser || !plotDiv || !popPeriod) return;
    
    loading = true;
    error = null;
    
    try {
      const plotlyModule = await initPlotly();
      if (!plotlyModule) {
        throw new Error('Failed to load Plotly module');
      }

      plotlyModule.purge(plotDiv);

      const scoringData = await fetchData(popPeriod);
      
      if (!hasData(scoringData)) {
        console.warn(`No scoring data available for PopPeriod ${popPeriod.id}`);
        return;
      }

      const colors = getThemeColors();
      const trace = createTrace(scoringData, colors);
      const layout = createLayout(colors);

      await plotlyModule.newPlot(plotDiv, [trace], layout, { 
        responsive: true,
        displayModeBar: false
      });
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      error = errorMessage;
      console.error('Plot rendering error:', err);
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    refreshTrigger;
    renderPlot();
  });
</script>

<div class="bg-light border border-light-alt rounded-lg p-4 w-full h-96 relative">
  <div bind:this={plotDiv} class="w-full h-full"></div>
  {#if loading}
    <div class="absolute inset-0 flex items-center justify-center bg-light bg-opacity-90 text-dark">
      Loading...
    </div>
  {:else if error}
    <div class="absolute inset-0 flex items-center justify-center bg-light bg-opacity-90 text-failure text-sm">
      {error}
    </div>
  {:else if !plotDiv?.hasChildNodes()}
    <div class="absolute inset-0 flex items-center justify-center text-dark text-sm">
      No scoring data available
    </div>
  {/if}
</div>