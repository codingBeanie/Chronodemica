export interface FieldMeta {
  min: number;
  max: number;
  step?: number;
  description?: string;
  hint?: string;
  type: 'input' | 'slider';
}

export interface PopPeriodFieldMeta {
  population: FieldMeta;
  social_orientation: FieldMeta;
  economic_orientation: FieldMeta;
  max_political_distance: FieldMeta;
  variety_tolerance: FieldMeta;
  non_voters_distance: FieldMeta;
  small_party_distance: FieldMeta;
  ratio_eligible: FieldMeta;
}

export interface PartyPeriodFieldMeta {
  social_orientation: FieldMeta;
  economic_orientation: FieldMeta;
  political_strength: FieldMeta;
}

export const POP_PERIOD_FIELD_META: PopPeriodFieldMeta = {
  population: {
    min: 0,
    max: 100000000,
    step: 1000,
    hint: "Total number of people in this population group",
    type: "input"
  },
  social_orientation: {
    min: -100,
    max: 100,
    step: 1,
    hint: "Social orientation from conservative (-100) to progressive (100)",
    type: "slider"
  },
  economic_orientation: {
    min: -100,
    max: 100,
    step: 1,
    hint: "Economic orientation from left-wing (-100) to right-wing (100)",
    type: "slider"
  },
  max_political_distance: {
    min: 0,
    max: 100,
    step: 1,
    hint: "Maximum distance on political compass before not voting",
    type: "slider"
  },
  variety_tolerance: {
    min: 0,
    max: 100,
    step: 1,
    hint: "How much political diversity this group accepts",
    type: "slider"
  },
  non_voters_distance: {
    min: 0,
    max: 100,
    step: 1,
    hint: "Political distance at which people abstain from voting",
    type: "slider"
  },
  small_party_distance: {
    min: 0,
    max: 100,
    step: 1,
    hint: "Distance at which voters prefer smaller parties over major ones",
    type: "slider"
  },
  ratio_eligible: {
    min: 0,
    max: 1,
    step: 0.01,
    hint: "Percentage of population eligible to vote (as decimal)",
    type: "slider"
  }
};

export const PARTY_PERIOD_FIELD_META: PartyPeriodFieldMeta = {
  social_orientation: {
    min: -100,
    max: 100,
    step: 1,
    hint: "Party's stance on social issues from conservative (-100) to progressive (100)",
    type: "slider"
  },
  economic_orientation: {
    min: -100,
    max: 100,
    step: 1,
    hint: "Party's economic policy from left-wing (-100) to right-wing (100)",
    type: "slider"
  },
  political_strength: {
    min: 0,
    max: 100,
    step: 1,
    hint: "Overall political influence and campaign effectiveness",
    type: "slider"
  }
};

export function getFieldMeta(fieldName: string, dataModelType: string): FieldMeta | null {
  if (dataModelType === 'PopPeriod') {
    return POP_PERIOD_FIELD_META[fieldName as keyof PopPeriodFieldMeta] || null;
  } else if (dataModelType === 'PartyPeriod') {
    return PARTY_PERIOD_FIELD_META[fieldName as keyof PartyPeriodFieldMeta] || null;
  }
  return null;
}