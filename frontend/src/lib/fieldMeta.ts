export interface FieldMeta {
  min: number;
  max: number;
  step?: number;
  description?: string;
  hint?: string;
  type: 'input' | 'slider';
  showRatio?: boolean;
  defaultValue?: number;
  minLabel?: string;
  maxLabel?: string;
}

export interface PopPeriodFieldMeta {
  pop_size: FieldMeta;
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

export interface ElectionFieldMeta {
  seats: FieldMeta;
  threshold: FieldMeta;
}

export const POP_PERIOD_FIELD_META: PopPeriodFieldMeta = {
  pop_size: {
    min: 0,
    max: 100,
    step: 1,
    hint: "Relative population weight (system calculates percentages automatically)",
    type: "slider",
    showRatio: true
  },
  social_orientation: {
    min: -100,
    max: 100,
    step: 1,
    hint: "Social orientation from libertarian (-100) to authoritarian (100)",
    type: "slider",
    minLabel: "libertarian",
    maxLabel: "authoritarian"
  },
  economic_orientation: {
    min: -100,
    max: 100,
    step: 1,
    hint: "Economic orientation from collectivist (-100) to individualist (100)",
    type: "slider",
    minLabel: "collectivist",
    maxLabel: "individualist"
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
    max: 100,
    step: 1,
    hint: "Percentage of population eligible to vote (as decimal)",
    type: "slider"
  }
};

export const PARTY_PERIOD_FIELD_META: PartyPeriodFieldMeta = {
  social_orientation: {
    min: -100,
    max: 100,
    step: 1,
    hint: "Party's stance on social issues from libertarian (-100) to authoritarian (100)",
    type: "slider",
    minLabel: "libertarian",
    maxLabel: "authoritarian"
  },
  economic_orientation: {
    min: -100,
    max: 100,
    step: 1,
    hint: "Party's economic policy from collectivist (-100) to individualist (100)",
    type: "slider",
    minLabel: "collectivist",
    maxLabel: "individualist"
  },
  political_strength: {
    min: 0,
    max: 100,
    step: 1,
    hint: "Overall political influence and campaign effectiveness",
    type: "slider"
  }
};

export const ELECTION_FIELD_META: ElectionFieldMeta = {
  seats: {
    min: 10,
    max: 1000,
    step: 1,
    hint: "Total number of seats in parliament",
    type: "input",
    defaultValue: 100
  },
  threshold: {
    min: 0,
    max: 100,
    step: 1,
    hint: "Minimum percentage required to enter parliament",
    type: "input",
    defaultValue: 5
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