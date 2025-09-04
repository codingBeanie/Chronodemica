<script lang="ts">
  import { browser } from '$app/environment';
  import { getPartyOrientations, getPopOrientations } from '../../lib/api/plotting';

  const { period, refreshTrigger } = $props<{ period: number; refreshTrigger?: number }>();

  let plotDiv: HTMLDivElement;
  let loading = $state(false);
  let Plotly: any = null;

  // Get theme colors from CSS custom properties
  function getThemeColors() {
    const root = document.documentElement;
    const getColor = (varName: string) => getComputedStyle(root).getPropertyValue(varName).trim();
    
    return {
      accent: getColor('--accent'),
      dark: getColor('--dark'),
      darkAlt: getColor('--dark-alt'),
      light: getColor('--light'),
      lightAlt: getColor('--light-alt'),
      success: getColor('--success'),
      failure: getColor('--failure')
    };
  }

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

    // Get current theme colors
    const colors = getThemeColors();
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
          color: partyData.colors && partyData.colors.length > 0 ? partyData.colors : colors.accent,
          size: partyData.size,
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
          color: colors.dark,
          size: popData.size,
          symbol: 'diamond'
        }
      });
    }

    const layout = {
      xaxis: { 
        range: [-120, 120],
        showticklabels: false,
        zeroline: true
      },
      yaxis: { 
        range: [-120, 120],
        showticklabels: false,
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
      annotations: [
        {
          x: -100,
          y: 120,
          text: 'Collectivist<br>Authoritarian',
          showarrow: false,
          font: { size: 10, color: colors.dark },
          xanchor: 'center',
          yanchor: 'middle'
        },
        {
          x: 100,
          y: 120,
          text: 'Market<br>Authoritarian',
          showarrow: false,
          font: { size: 10, color: colors.dark },
          xanchor: 'center',
          yanchor: 'middle'
        },
        {
          x: -100,
          y: -110,
          text: 'Collectivist<br>Libertarian',
          showarrow: false,
          font: { size: 10, color: colors.dark },
          xanchor: 'center',
          yanchor: 'middle'
        },
        {
          x: 100,
          y: -110,
          text: 'Market<br>Libertarian',
          showarrow: false,
          font: { size: 10, color: colors.dark },
          xanchor: 'center',
          yanchor: 'middle'
        }
      ],
      margin: { t: 10, l: 10, r: 10, b: 10 },
      paper_bgcolor: colors.light,
      plot_bgcolor: colors.light,
      font: { color: colors.dark, size: 12 }
    };

    plotlyModule.newPlot(plotDiv, traces, layout, { 
      responsive: true,
      displayModeBar: false
    });
    
    loading = false;
  }

  $effect(() => {
    // React to period or refreshTrigger changes
    refreshTrigger; // Make the effect reactive to refreshTrigger changes
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