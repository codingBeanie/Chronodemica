<script lang="ts">
  import { browser } from '$app/environment';
  import type { EnrichedElectionResult } from '../../lib/api/data_services/simulation';
  import { processElectionResults, type ElectionBarData } from '../../lib/api/data_services/plotting';

  interface ThemeColors {
    accent: string;
    dark: string;
    darkAlt: string;
    light: string;
    lightAlt: string;
    success: string;
    failure: string;
  }

  const { electionResults, threshold, aspectRatio = 2.5, previousElectionResults = null } = $props<{ 
    electionResults: EnrichedElectionResult[]; 
    threshold: number; 
    aspectRatio?: number;
    previousElectionResults?: EnrichedElectionResult[] | null;
  }>();

  // Central configuration
  const PLOT_CONFIG = {
    MARGIN: { t: 0, l: 40, r: 10, b: 40 } as const,
    FONT_SIZE: { tick: 18, default: 16, title: 18, annotation: 18, percentage: 22, change: 16 } as const,
    BAR_CONFIG: {
      opacity: 0.9,
      line: { width: 0 }
    } as const
  };

  let plotDiv: HTMLDivElement;
  let containerDiv: HTMLDivElement;
  let loading = $state(false);
  let error = $state<string | null>(null);
  let Plotly: any = null;
  let containerHeight = $state(400); // Default height

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

  function updateContainerHeight() {
    if (!containerDiv) return;
    const containerWidth = containerDiv.offsetWidth;
    containerHeight = containerWidth / aspectRatio;
  }

  function calculatePeriodChanges(currentResults: EnrichedElectionResult[], previousResults: EnrichedElectionResult[] | null) {
    if (!previousResults) return null;
    
    const changes: { [key: string]: string } = {};
    
    // Create lookup map for previous results by party name
    const previousMap = new Map<string, number>();
    previousResults.forEach(result => {
      if (result.percentage !== null && result.percentage !== undefined) {
        previousMap.set(result.party_name, result.percentage);
      }
    });
    
    // Calculate changes for current results
    currentResults.forEach(result => {
      if (result.percentage !== null && result.percentage !== undefined) {
        const previousPercentage = previousMap.get(result.party_name);
        
        if (previousPercentage !== undefined) {
          const change = result.percentage - previousPercentage;
          if (Math.abs(change) < 0.1) {
            changes[result.party_name] = "±0.0";
          } else {
            const sign = change > 0 ? "+" : "";
            changes[result.party_name] = `${sign}${change.toFixed(1)}`;
          }
        } else {
          changes[result.party_name] = "(-)";
        }
      }
    });
    
    return changes;
  }


  function createTrace(data: ElectionBarData, colors: ThemeColors) {
    return {
      x: data.x,
      y: data.y,
      type: 'bar',
      hovertemplate: '%{x}: %{y:.1f}%<extra></extra>',
      marker: {
        color: data.colors,
        opacity: PLOT_CONFIG.BAR_CONFIG.opacity,
        line: {
          color: colors.dark,
          width: PLOT_CONFIG.BAR_CONFIG.line.width
        }
      }
    };
  }

  function createLayout(data: ElectionBarData, colors: ThemeColors) {
    // Calculate the maximum value for y-axis range to ensure text is visible but reduce whitespace
    const maxValue = Math.max(...data.y);
    const yAxisMax = maxValue * 1.2; // Reduce padding from 15% to 8%
    
    // Calculate period changes
    const changes = calculatePeriodChanges(electionResults, previousElectionResults);
    
    return {
      xaxis: {
        tickangle: 0, // No rotation
        tickfont: { size: PLOT_CONFIG.FONT_SIZE.tick, color: colors.darkAlt },
        ticklen: 10, // Length of tick marks
        tickcolor: 'transparent' // Hide tick marks to create visual space
      },
      yaxis: {
        tickfont: { size: PLOT_CONFIG.FONT_SIZE.tick, color: colors.darkAlt },
        range: [0, yAxisMax]
      },
      showlegend: false,
      margin: PLOT_CONFIG.MARGIN,
      paper_bgcolor: colors.light,
      plot_bgcolor: colors.light,
      font: { color: colors.dark, size: PLOT_CONFIG.FONT_SIZE.default, family: 'Noto Sans, sans-serif' },
      shapes: [
        {
          type: 'line',
          x0: 0,
          x1: 1,
          y0: threshold,
          y1: threshold,
          xref: 'paper',
          yref: 'y',
          line: {
            color: colors.dark, // Use theme color instead of hardcoded failure color
            width: 2,
            opacity:1,
            dash: 'dash'
          },
          layer: 'below' // Put line behind the bars
        }
      ],
      annotations: [
        {
          text: `Voter Turnout: ${data.voterTurnout.toFixed(1)}%`,
          x: 1,
          y: 1,
          xref: 'paper',
          yref: 'paper',
          xanchor: 'right',
          yanchor: 'top',
          showarrow: false,
          font: { size: PLOT_CONFIG.FONT_SIZE.annotation, color: colors.darkAlt, family: 'Noto Sans, sans-serif' },
          bgcolor: colors.light,
          bordercolor: colors.darkAlt,
          borderwidth: 0,
          borderpad: 12
        },
        // Percentage labels with light backgrounds
        ...data.x.map((_, index) => ({
          text: `<b>${data.text[index]}</b>`,
          x: index,
          y: data.y[index] + (yAxisMax * 0.04), // Slightly above the bar
          xref: 'x',
          yref: 'y',
          xanchor: 'center',
          yanchor: 'bottom',
          showarrow: false,
          font: { size: PLOT_CONFIG.FONT_SIZE.percentage, color: colors.darkAlt, family: 'Noto Sans, sans-serif' },
          bgcolor: colors.light,
          bordercolor: colors.light,
          borderwidth: 1,
          borderpad: 4
        })),
        // Change indicators below percentages (only if changes exist)
        ...(changes ? data.x.map((_, index) => {
          const partyName = data.x[index];
          const changeText = changes[partyName] || "(-)";
          return {
            text: changeText,
            x: index,
            y: data.y[index] + (yAxisMax * -0.0), // Below the percentage label
            xref: 'x',
            yref: 'y',
            xanchor: 'center',
            yanchor: 'bottom',
            showarrow: false,
            font: { size: PLOT_CONFIG.FONT_SIZE.change, color: colors.darkAlt, family: 'Noto Sans, sans-serif' },
            bgcolor: 'transparent',
            borderwidth: 0
          };
        }) : [])
      ]
    };
  }

  function hasData(results: EnrichedElectionResult[]): boolean {
    return results.some(r => (r.party_id > 0 || r.party_id === -2) && (r.percentage || 0) > 0);
  }

  async function renderPlot() {
    if (!browser || !plotDiv || !electionResults?.length) return;
    
    loading = true;
    error = null;
    
    try {
      const plotlyModule = await initPlotly();
      if (!plotlyModule) {
        throw new Error('Failed to load Plotly module');
      }

      plotlyModule.purge(plotDiv);
      
      if (!hasData(electionResults)) {
        console.warn('No valid election data available');
        return;
      }

      const colors = getThemeColors();
      const data = processElectionResults(electionResults);
      const trace = createTrace(data, colors);
      const layout = createLayout(data, colors);

      await plotlyModule.newPlot(plotDiv, [trace], layout, { 
        responsive: true,
        displayModeBar: false
      });
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      error = errorMessage;
      console.error('Bar chart rendering error:', err);
    } finally {
      loading = false;
    }
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

  $effect(() => {
    renderPlot();
  });
</script>

<div 
  bind:this={containerDiv}
  class="bg-light border border-light-alt rounded-lg p-4 w-full relative"
  style="height: {containerHeight}px;"
>
  <div bind:this={plotDiv} class="w-full h-full"></div>
  {#if loading}
    <div class="absolute inset-0 flex items-center justify-center bg-light bg-opacity-90 text-dark">
      Loading...
    </div>
  {:else if error}
    <div class="absolute inset-0 flex items-center justify-center bg-light bg-opacity-90 text-failure text-sm">
      {error}
    </div>
  {:else if !electionResults?.length || !hasData(electionResults)}
    <div class="absolute inset-0 flex items-center justify-center text-dark text-sm">
      No election results available
    </div>
  {/if}
</div>