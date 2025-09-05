<script lang="ts">
  import { browser } from '$app/environment';
  import { getPartyOrientations, getPopOrientations } from '../../lib/api/data_services/plotting';

  interface PlotData {
    x: number[];
    y: number[];
    text: string[];
    size: number[];
    colors?: string[];
  }

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
    text: string[];
    name: string;
    type: string;
    mode: string;
    marker: {
      color: string | string[];
      size: number[];
      symbol: string;
    };
  }

  const { period, refreshTrigger } = $props<{ period: number; refreshTrigger?: number }>();

  // Central configuration
  const PLOT_CONFIG = {
    AXIS_RANGE: [-120, 120] as const,
    MARGIN: { t: 10, l: 10, r: 10, b: 10 } as const,
    FONT_SIZE: { annotation: 10, default: 12 } as const,
    LEGEND: {
      orientation: 'h' as const,
      x: 0.5,
      xanchor: 'center' as const,
      y: 1.02,
      yanchor: 'bottom' as const
    },
    ANNOTATIONS: [
      { x: -100, y: 120, text: 'Collectivist<br>Authoritarian' },
      { x: 100, y: 120, text: 'Market<br>Authoritarian' },
      { x: -100, y: -110, text: 'Collectivist<br>Libertarian' },
      { x: 100, y: -110, text: 'Market<br>Libertarian' }
    ] as const,
    MARKERS: {
      party: { symbol: 'circle' as const },
      population: { symbol: 'diamond' as const }
    } as const
  };

  const CSS_VARIABLES = ['--accent', '--dark', '--dark-alt', '--light', '--light-alt', '--success', '--failure'] as const;

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

  function createTraces(partyData: PlotData, popData: PlotData, colors: ThemeColors): PlotTrace[] {
    const traces: PlotTrace[] = [];
    
    if (partyData.x.length > 0) {
      traces.push({
        x: partyData.x,
        y: partyData.y,
        text: partyData.text,
        name: 'Parties',
        type: 'scatter',
        mode: 'markers',
        marker: { 
          color: partyData.colors?.length ? partyData.colors : colors.accent,
          size: partyData.size,
          symbol: PLOT_CONFIG.MARKERS.party.symbol
        }
      });
    }
    
    if (popData.x.length > 0) {
      traces.push({
        x: popData.x,
        y: popData.y,
        text: popData.text,
        name: 'Populations',
        type: 'scatter',
        mode: 'markers',
        marker: { 
          color: colors.dark,
          size: popData.size,
          symbol: PLOT_CONFIG.MARKERS.population.symbol
        }
      });
    }

    return traces;
  }

  function createLayout(colors: ThemeColors) {
    return {
      xaxis: { 
        range: PLOT_CONFIG.AXIS_RANGE,
        showticklabels: false,
        zeroline: true
      },
      yaxis: { 
        range: PLOT_CONFIG.AXIS_RANGE,
        showticklabels: false,
        zeroline: true
      },
      showlegend: true,
      legend: PLOT_CONFIG.LEGEND,
      annotations: PLOT_CONFIG.ANNOTATIONS.map(annotation => ({
        ...annotation,
        showarrow: false,
        font: { size: PLOT_CONFIG.FONT_SIZE.annotation, color: colors.dark },
        xanchor: 'center' as const,
        yanchor: 'middle' as const
      })),
      margin: PLOT_CONFIG.MARGIN,
      paper_bgcolor: colors.light,
      plot_bgcolor: colors.light,
      font: { color: colors.dark, size: PLOT_CONFIG.FONT_SIZE.default }
    };
  }

  async function fetchData(period: number): Promise<[PlotData, PlotData]> {
    try {
      const [partyData, popData] = await Promise.all([
        getPartyOrientations(period),
        getPopOrientations(period)
      ]);
      return [partyData, popData];
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch plot data';
      throw new Error(errorMessage);
    }
  }

  function hasData(partyData: PlotData, popData: PlotData): boolean {
    return partyData.x.length > 0 || popData.x.length > 0;
  }

  async function renderPlot() {
    if (!browser || !plotDiv || !period || period <= 0) return;
    
    loading = true;
    error = null;
    
    try {
      const plotlyModule = await initPlotly();
      if (!plotlyModule) {
        throw new Error('Failed to load Plotly module');
      }

      plotlyModule.purge(plotDiv);

      const [partyData, popData] = await fetchData(period);
      
      if (!hasData(partyData, popData)) {
        console.warn(`No data available for period ${period}`);
        return;
      }

      const colors = getThemeColors();
      const traces = createTraces(partyData, popData, colors);
      const layout = createLayout(colors);

      await plotlyModule.newPlot(plotDiv, traces, layout, { 
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
      No data available for period {period}
    </div>
  {/if}
</div>