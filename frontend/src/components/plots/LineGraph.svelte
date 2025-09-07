<script lang="ts">
  import { browser } from '$app/environment';
  import { getPartyResultsOverTime, getPopulationVotingBehavior, type LineGraphData } from '../../lib/api/data_services/plotting';

  interface ThemeColors {
    accent: string;
    dark: string;
    darkAlt: string;
    light: string;
    lightAlt: string;
    success: string;
    failure: string;
  }

  interface Props {
    partyId?: number;
    popId?: number;
    mode?: 'party' | 'population';
    aspectRatio?: number;
  }

  const { partyId, popId, mode = 'party', aspectRatio = 2.5 } = $props<Props>();

  // Central configuration
  const PLOT_CONFIG = {
    MARGIN: { t: 0, l: 50, r: 10, b: 60 } as const,
    FONT_SIZE: { tick: 18, default: 16, title: 18, annotation: 18 } as const,
    LINE_CONFIG: {
      width: 3,
      mode: 'lines+markers',
      marker: { size: 8 }
    } as const
  } as const;

  // State
  let plotDiv: HTMLDivElement;
  let containerDiv: HTMLDivElement;
  let loading = $state(true);
  let error = $state<string | null>(null);
  let lineData = $state<LineGraphData>({ traces: [], periods: [] });
  let Plotly: any = null;
  let containerHeight = $state(400);

  // Theme and styling functions
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

  function updateContainerHeight() {
    if (!containerDiv) return;
    const containerWidth = containerDiv.offsetWidth;
    containerHeight = containerWidth / aspectRatio;
  }

  // Plotly initialization
  async function initPlotly() {
    if (!Plotly && browser) {
      Plotly = await import('plotly.js-dist-min');
    }
    return Plotly;
  }

  // Data fetching
  async function fetchData() {
    if (!browser) return;
    
    loading = true;
    error = null;
    
    try {
      const data = await (mode === 'population' && popId !== undefined
        ? getPopulationVotingBehavior(popId)
        : getPartyResultsOverTime(partyId)
      );
      
      console.log(`LineGraph - Fetched ${mode} data:`, data);
      lineData = data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch data';
      error = errorMessage;
      console.error('Error fetching line graph data:', err);
    } finally {
      loading = false;
    }
  }

  // Data validation
  function hasData(data: LineGraphData): boolean {
    return data.traces.length > 0 && data.traces.some(trace => trace.y.some(value => value !== null && value > 0));
  }

  // Plotly configuration functions
  function createTraces(data: LineGraphData, colors: ThemeColors) {
    return data.traces.map(trace => ({
      x: trace.x,
      y: trace.y,
      type: 'scatter',
      mode: PLOT_CONFIG.LINE_CONFIG.mode,
      name: trace.name,
      line: {
        color: trace.color,
        width: PLOT_CONFIG.LINE_CONFIG.width
      },
      marker: {
        color: trace.color,
        size: PLOT_CONFIG.LINE_CONFIG.marker.size,
        line: {
          color: colors.light,
          width: 1
        }
      },
      hovertemplate: `<b>${trace.name}</b><br>%{x}: %{y:.1f}%<extra></extra>`
    }));
  }

  function createLayout(data: LineGraphData, colors: ThemeColors) {
    return {
      xaxis: {
        title: 'Period',
        titlefont: { size: PLOT_CONFIG.FONT_SIZE.title, color: colors.darkAlt },
        tickfont: { size: PLOT_CONFIG.FONT_SIZE.tick, color: colors.darkAlt },
        tickangle: -45,
        ticklen: 10,
        tickcolor: 'transparent',
        type: 'category'
      },
      yaxis: {
        title: mode === 'population' ? 'Voting Behavior (%)' : 'Election Results (%)',
        titlefont: { size: PLOT_CONFIG.FONT_SIZE.title, color: colors.darkAlt },
        tickfont: { size: PLOT_CONFIG.FONT_SIZE.tick, color: colors.darkAlt },
        rangemode: 'tozero',
        autorange: true,
        ticksuffix: '%'
      },
      showlegend: data.traces.length > 1,
      legend: {
        x: 0.5,
        y: 1.15,
        xanchor: 'center',
        yanchor: 'bottom',
        orientation: 'h',
        bgcolor: colors.light,
        bordercolor: colors.darkAlt,
        borderwidth: 1,
        font: { size: PLOT_CONFIG.FONT_SIZE.default, color: colors.dark }
      },
      margin: PLOT_CONFIG.MARGIN,
      paper_bgcolor: colors.light,
      plot_bgcolor: colors.light,
      font: { color: colors.dark, size: PLOT_CONFIG.FONT_SIZE.default, family: 'Noto Sans, sans-serif' },
      hovermode: 'x unified',
      uirevision: 'constant' // Preserve UI state during updates
    };
  }

  // Main rendering function
  async function renderPlot() {
    if (!browser || !plotDiv || !lineData.traces.length) return;
    
    try {
      const plotlyModule = await initPlotly();
      if (!plotlyModule) {
        throw new Error('Failed to load Plotly module');
      }

      plotlyModule.purge(plotDiv);
      
      if (!hasData(lineData)) {
        console.warn('No valid line graph data available');
        return;
      }

      const colors = getThemeColors();
      const traces = createTraces(lineData, colors);
      const layout = createLayout(lineData, colors);

      await plotlyModule.newPlot(plotDiv, traces, layout, { 
        responsive: true,
        displayModeBar: false
      });
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      error = errorMessage;
      console.error('Line graph rendering error:', err);
    }
  }

  // Helper functions for template
  function getLoadingMessage(): string {
    return mode === 'population' ? 'Loading population voting data...' : 'Loading party results...';
  }

  function getNoDataMessage(): string {
    return mode === 'population' ? 'No population voting data available' : 'No party results data available';
  }

  // Handle resize and initial setup
  $effect(() => {
    if (!browser || !containerDiv) return;
    
    updateContainerHeight();
    
    const resizeObserver = new ResizeObserver(() => {
      updateContainerHeight();
      renderPlot();
    });
    
    resizeObserver.observe(containerDiv);
    
    return () => {
      resizeObserver.disconnect();
    };
  });

  // Fetch data when component mounts or partyId/popId changes
  $effect(() => {
    fetchData();
  });

  // Render plot when data changes
  $effect(() => {
    if (lineData.traces.length > 0) {
      renderPlot();
    }
  });
</script>

<div 
  bind:this={containerDiv}
  class="relative w-full p-4 border rounded-lg bg-light border-light-alt"
  style="height: {containerHeight}px;"
>
  <div bind:this={plotDiv} class="w-full h-full"></div>
  {#if loading}
    <div class="absolute inset-0 flex items-center justify-center bg-light bg-opacity-90 text-dark">
      {getLoadingMessage()}
    </div>
  {:else if error}
    <div class="absolute inset-0 flex items-center justify-center text-sm bg-light bg-opacity-90 text-failure">
      {error}
    </div>
  {:else if !lineData.traces.length || !hasData(lineData)}
    <div class="absolute inset-0 flex items-center justify-center text-sm text-dark">
      {getNoDataMessage()}
    </div>
  {/if}
</div>