<script lang="ts">
  import { browser } from '$app/environment';
  import { getPartyOrientations, getPopOrientations } from '../../lib/api/plotting';

  const { period } = $props<{ period: number }>();

  let plotDiv: HTMLDivElement;
  let loading = $state(false);
  let Plotly: any = null;

  // Static theme colors - simpler and more reliable
  const COLORS = {
    accent: '#3182ce',
    dark: '#2d3748',
    light: '#f8f9fa'
  };

  async function initPlotly() {
    if (!Plotly && browser) {
      Plotly = await import('plotly.js-dist-min');
    }
    return Plotly;
  }

  async function renderPlot() {
    if (!browser || !plotDiv || !period || period <= 0) return;
    
    loading = true;
    
    const plotlyModule = await initPlotly();
    if (!plotlyModule) return;

    // Clear existing plot
    plotlyModule.purge(plotDiv);

    const [partyData, popData] = await Promise.all([
      getPartyOrientations(period),
      getPopOrientations(period)
    ]);

    console.log('Party data:', partyData);
    console.log('Pop data:', popData);
    
    // Check if we have any data
    if (partyData.x.length === 0 && popData.x.length === 0) {
      console.warn('No data to display');
      loading = false;
      return;
    }

    const traces = [];
    
    // Add party trace if data exists
    if (partyData.x.length > 0) {
      traces.push({
        x: partyData.x,
        y: partyData.y,
        text: partyData.text,
        name: 'Parties',
        type: 'scatter',
        mode: 'markers',
        marker: { 
          color: COLORS.accent,
          size: partyData.size.map(s => Math.max(s * 1, 8)),
          symbol: 'circle'
        }
      });
    }
    
    // Add pop trace if data exists
    if (popData.x.length > 0) {
      traces.push({
        x: popData.x,
        y: popData.y,
        text: popData.text,
        name: 'Populations',
        type: 'scatter',
        mode: 'markers',
        marker: { 
          color: COLORS.dark,
          size: popData.size.map(s => Math.max(s / 1, 8)),
          symbol: 'diamond'
        }
      });
    }

    const layout = {
      xaxis: { 
        title: 'Economic Orientation',
        range: [-100, 100],
        showticklabels: true,
        zeroline: true
      },
      yaxis: { 
        title: 'Social Orientation',
        range: [-100, 100],
        showticklabels: true,
        zeroline: true
      },
      showlegend: true,
      legend: {
        orientation: 'h',
        x: 0.5,
        xanchor: 'center',
        y: 1.02,
        yanchor: 'bottom'
      },
      margin: { t: 0, l: 0, r: 0, b: 0 },
      paper_bgcolor: COLORS.light,
      plot_bgcolor: COLORS.light,
      font: { color: COLORS.dark, size: 12 }
    };

    plotlyModule.newPlot(plotDiv, traces, layout, { 
      responsive: true,
      displayModeBar: false
    });
    
    loading = false;
  }

  $effect(() => {
    renderPlot();
  });
</script>

<div class="bg-light border border-light-alt rounded-lg p-4 w-full h-96 relative">
  <div bind:this={plotDiv} class="w-full h-full"></div>
  {#if loading}
    <div class="absolute inset-0 flex items-center justify-center bg-light bg-opacity-90 text-dark">
      Loading...
    </div>
  {:else if !plotDiv?.hasChildNodes()}
    <div class="absolute inset-0 flex items-center justify-center text-dark text-sm">
      No data available for period {period}
    </div>
  {/if}
</div>