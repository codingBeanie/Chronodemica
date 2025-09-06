<script lang="ts">
  import { getCoalitions, makeGovernment, cancelGovernment, type Coalition } from '$lib/api/data_services/simulation';
  import Button from '../ui/Button.svelte';

  // Props
  let {
    periodId,
    onGovernmentChange
  }: {
    periodId: number | null;
    onGovernmentChange?: () => void;
  } = $props();

  // State
  let coalitions = $state<Coalition[]>([]);
  let loading = $state(false);
  let error = $state('');

  // Load coalitions when component mounts or periodId changes
  $effect(() => {
    if (periodId) {
      loadCoalitions();
    }
  });

  async function loadCoalitions() {
    if (!periodId) return;
    
    loading = true;
    error = '';
    
    try {
      const response = await getCoalitions(periodId);
      
      if (response.success && response.data) {
        coalitions = response.data;
      } else {
        error = response.error || 'Failed to load coalitions';
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred loading coalitions';
    } finally {
      loading = false;
    }
  }

  async function handleMakeGovernment(coalition: Coalition) {
    if (!periodId) return;
    
    loading = true;
    error = '';
    
    try {
      const partyIds = coalition.parties.map(party => party.party_id);
      const response = await makeGovernment(periodId, partyIds);
      
      if (response.success) {
        // Show success message or reload data
        console.log('Government formed successfully:', response.data);
        // Optionally reload coalitions to update the display
        await loadCoalitions();
        // Notify parent to update seats overview
        onGovernmentChange?.();
      } else {
        error = response.error || 'Failed to form government';
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred forming government';
    } finally {
      loading = false;
    }
  }

  function isCoalitionInGovernment(coalition: Coalition): boolean {
    return coalition.parties.every(party => party.in_government);
  }

  async function handleCancelGovernment(coalition: Coalition) {
    if (!periodId) return;
    
    loading = true;
    error = '';
    
    try {
      const partyIds = coalition.parties.map(party => party.party_id);
      const response = await cancelGovernment(periodId, partyIds);
      
      if (response.success) {
        console.log('Government cancelled successfully:', response.data);
        await loadCoalitions();
        // Notify parent to update seats overview
        onGovernmentChange?.();
      } else {
        error = response.error || 'Failed to cancel government';
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred cancelling government';
    } finally {
      loading = false;
    }
  }
</script>

<div class="w-full p-2">
  {#if loading}
    <div class="text-dark">Loading coalitions...</div>
  {:else if error}
    <div class="text-failure p-4 bg-light border border-failure rounded-md">
      Error: {error}
    </div>
  {:else if coalitions.length === 0}
    <div class="text-dark p-4 bg-light-alt border border-light-alt rounded-md">
      No coalition data available. Run a simulation first.
    </div>
  {:else}
    <div class="w-full h-full overflow-y-auto space-y-6">
      {#each coalitions as coalition (coalition.coalition_id)}
        <div class="p-4 bg-light border border-light-alt rounded-md transition-shadow duration-200 hover:shadow-lg">
          <!-- Coalition Header -->
          <div class="mb-4">
            <div class="text-lg font-bold text-dark mb-1">
              {coalition.coalition_name}
            </div>
            <div class="text-base font-medium text-dark-alt mb-3">
              {coalition.total_seats} seats • {coalition.total_percentage.toFixed(1)}% • +{coalition.majority_margin} majority
            </div>
          </div>
          
          <!-- Parties Section -->
          <div class="space-y-3">
            <div class="text-base font-semibold text-dark border-b border-light-alt pb-1">
              Coalition Members
            </div>
            <div class="space-y-2">
              {#each coalition.parties as party (party.party_id)}
                <div class="p-3 bg-light-alt rounded">
                  <div class="flex items-center space-x-3 mb-2">
                    <div 
                      class="w-5 h-5 rounded-full flex-shrink-0"
                      style="background-color: {party.color || 'var(--dark-alt)'}"
                    ></div>
                    <div class="flex items-center gap-2">
                      {#if party.in_government}
                        <i class="bi bi-bank2 text-accent" title={party.head_of_government ? "Head of Government" : "In Government"}></i>
                      {/if}
                      <span class="text-base font-semibold text-dark">{party.name}</span>
                    </div>
                  </div>
                  <div class="text-left">
                    <span class="text-sm text-dark-alt">{party.seats} seats • {party.percentage.toFixed(1)}%</span>
                  </div>
                </div>
              {/each}
            </div>
            
            <!-- Action Button -->
            <div class="mt-4 pt-3 border-t border-light-alt">
              <Button 
                text={isCoalitionInGovernment(coalition) ? "Cancel Government" : "Make Government"}
                theme={isCoalitionInGovernment(coalition) ? "failure" : "accent"}
                onclick={() => isCoalitionInGovernment(coalition) ? handleCancelGovernment(coalition) : handleMakeGovernment(coalition)}
              />
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>