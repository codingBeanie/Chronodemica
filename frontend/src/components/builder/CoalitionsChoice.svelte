<script lang="ts">
  import { getCoalitions, makeGovernment, cancelGovernment, type Coalition, type CoalitionParty } from '$lib/api/data_services/simulation';
  import Button from '../ui/Button.svelte';

  // Props interface
  interface Props {
    periodId: number | null;
    onGovernmentChange?: () => void;
  }

  let { periodId, onGovernmentChange }: Props = $props();

  // Component state
  let coalitions = $state<Coalition[]>([]);
  let loading = $state(false);
  let error = $state('');

  // Constants
  const DEFAULT_PARTY_COLOR = '#525252';
  const MESSAGES = {
    LOADING: 'Loading coalitions...',
    NO_DATA: 'No coalition data available. Run a simulation first.',
    LOAD_ERROR: 'Failed to load coalitions',
    GOVERNMENT_FORM_ERROR: 'Failed to form government',
    GOVERNMENT_CANCEL_ERROR: 'Failed to cancel government',
    LOAD_GENERIC_ERROR: 'An error occurred loading coalitions',
    GOVERNMENT_FORM_GENERIC_ERROR: 'An error occurred forming government',
    GOVERNMENT_CANCEL_GENERIC_ERROR: 'An error occurred cancelling government'
  } as const;

  // Load coalitions when periodId changes
  $effect(() => {
    if (periodId) {
      loadCoalitions();
    }
  });

  // Utility functions
  function isCoalitionInGovernment(coalition: Coalition): boolean {
    return coalition.parties.every(party => party.in_government);
  }

  function getPartyTooltip(party: CoalitionParty): string {
    const governmentStatus = party.in_government 
      ? ` • ${party.head_of_government ? 'Head of Government' : 'In Government'}`
      : '';
    return `${party.name}: ${party.seats} seats (${party.percentage.toFixed(1)}%)${governmentStatus}`;
  }

  function getButtonConfig(coalition: Coalition) {
    const inGovernment = isCoalitionInGovernment(coalition);
    return {
      text: inGovernment ? 'Cancel Government' : 'Make Government',
      theme: inGovernment ? 'failure' : 'accent',
      action: inGovernment ? handleCancelGovernment : handleMakeGovernment
    } as const;
  }

  // API functions
  async function loadCoalitions(): Promise<void> {
    if (!periodId) return;
    
    loading = true;
    error = '';
    
    try {
      const response = await getCoalitions(periodId);
      
      if (response.success && response.data) {
        coalitions = response.data;
      } else {
        error = response.error || MESSAGES.LOAD_ERROR;
      }
    } catch (err) {
      error = err instanceof Error ? err.message : MESSAGES.LOAD_GENERIC_ERROR;
    } finally {
      loading = false;
    }
  }

  async function handleGovernmentAction(
    coalition: Coalition, 
    action: typeof makeGovernment | typeof cancelGovernment,
    successMessage: string,
    errorMessage: string,
    genericErrorMessage: string
  ): Promise<void> {
    if (!periodId) return;
    
    loading = true;
    error = '';
    
    try {
      const partyIds = coalition.parties.map(party => party.party_id);
      const response = await action(periodId, partyIds);
      
      if (response.success) {
        console.log(successMessage, response.data);
        await loadCoalitions();
        onGovernmentChange?.();
      } else {
        error = response.error || errorMessage;
      }
    } catch (err) {
      error = err instanceof Error ? err.message : genericErrorMessage;
    } finally {
      loading = false;
    }
  }

  async function handleMakeGovernment(coalition: Coalition): Promise<void> {
    await handleGovernmentAction(
      coalition,
      makeGovernment,
      'Government formed successfully:',
      MESSAGES.GOVERNMENT_FORM_ERROR,
      MESSAGES.GOVERNMENT_FORM_GENERIC_ERROR
    );
  }

  async function handleCancelGovernment(coalition: Coalition): Promise<void> {
    await handleGovernmentAction(
      coalition,
      cancelGovernment,
      'Government cancelled successfully:',
      MESSAGES.GOVERNMENT_CANCEL_ERROR,
      MESSAGES.GOVERNMENT_CANCEL_GENERIC_ERROR
    );
  }
</script>

<!-- Component Container -->
<div class="w-full p-2">
  {#if loading}
    <!-- Loading State -->
    <div class="text-dark">{MESSAGES.LOADING}</div>
    
  {:else if error}
    <!-- Error State -->
    <div class="text-failure p-4 bg-light border border-failure rounded-md">
      Error: {error}
    </div>
    
  {:else if coalitions.length === 0}
    <!-- Empty State -->
    <div class="text-dark p-4 bg-light-alt border border-light-alt rounded-md">
      {MESSAGES.NO_DATA}
    </div>
    
  {:else}
    <!-- Coalitions List -->
    <div class="w-full h-full overflow-y-auto space-y-6">
      {#each coalitions as coalition (coalition.coalition_id)}
        {@const buttonConfig = getButtonConfig(coalition)}
        
        <!-- Coalition Card -->
        <div class="p-4 bg-light border border-light-alt rounded-md transition-shadow duration-200 hover:shadow-lg">
          
          <!-- Coalition Header -->
          <header class="mb-4">
            <h3 class="text-lg font-bold text-dark mb-1">
              {coalition.coalition_name}
            </h3>
            <div class="text-base font-medium text-dark-alt mb-3">
              {coalition.total_seats} seats • {coalition.total_percentage.toFixed(1)}% • +{coalition.majority_margin} majority
            </div>
          </header>
          
          <!-- Coalition Content -->
          <section class="space-y-3">
            <h4 class="text-base font-semibold text-dark border-b border-light-alt pb-1">
              Coalition Members
            </h4>
            
            <!-- Proportional Bar Chart -->
            <div class="flex w-full h-16 rounded overflow-hidden border border-light-alt">
              {#each coalition.parties as party (party.party_id)}
                <div 
                  class="flex flex-col items-center justify-center text-white text-xs font-medium relative hover:brightness-110 transition-all cursor-pointer min-w-8 px-1"
                  style="flex: {party.seats}; background-color: {party.color || DEFAULT_PARTY_COLOR}"
                  title={getPartyTooltip(party)}
                >
                  <!-- Party Name Row -->
                  <div class="flex items-center gap-1 mb-1">
                    {#if party.in_government}
                      <i class="bi bi-bank2 text-white" aria-label="In Government"></i>
                    {/if}
                    <span class="truncate text-center font-semibold">{party.name}</span>
                  </div>
                  
                  <!-- Party Stats Row -->
                  <div class="text-xs opacity-90">
                    {party.seats} seats • {party.percentage.toFixed(1)}%
                  </div>
                </div>
              {/each}
            </div>
            
            <!-- Government Action -->
            <footer class="mt-4 pt-3 border-t border-light-alt">
              <Button 
                text={buttonConfig.text}
                theme={buttonConfig.theme}
                onclick={() => buttonConfig.action(coalition)}
              />
            </footer>
          </section>
        </div>
      {/each}
    </div>
  {/if}
</div>