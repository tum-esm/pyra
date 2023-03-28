---
id: "components"
title: "Module: components"
sidebar_label: "components"
sidebar_position: 0
custom_edit_url: null
---

## Variables

### automationComponents

• **automationComponents**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `MeasurementDecisionStatus` | () => `Element` |
| `PyraCoreStatus` | () => `Element` |

#### Defined in

[components/automation/index.ts:4](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/components/automation/index.ts#L4)

___

### configurationComponents

• **configurationComponents**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `ConfigElementText` | (`props`: { `disabled?`: `boolean` ; `numeric?`: `boolean` ; `oldValue`: `string` \| `number` ; `postfix?`: `string` ; `showFileSelector?`: `boolean` ; `title`: `string` ; `value`: `string` \| `number` ; `setValue`: (`v`: `string` \| `number`) => `void`  }) => `Element` |
| `ConfigElementTime` | (`props`: { `disabled?`: `boolean` ; `oldValue`: { `hour`: `number` ; `minute`: `number` ; `second`: `number`  } ; `title`: `string` ; `value`: { `hour`: `number` ; `minute`: `number` ; `second`: `number`  } ; `setValue`: (`v`: { `hour`: `number` ; `minute`: `number` ; `second`: `number`  }) => `void`  }) => `Element` |
| `ConfigElementToggle` | (`props`: { `oldValue`: `boolean` ; `title`: `string` ; `value`: `boolean` ; `setValue`: (`v`: `boolean`) => `void`  }) => `Element` |
| `ConfigSectionCamtracker` | () => `Element` |
| `ConfigSectionErrorEmail` | () => `Element` |
| `ConfigSectionGeneral` | () => `Element` |
| `ConfigSectionHelios` | () => `Element` |
| `ConfigSectionMeasurementTriggers` | () => `Element` |
| `ConfigSectionOpus` | () => `Element` |
| `ConfigSectionTumPlc` | () => `Element` |
| `ConfigSectionUpload` | () => `Element` |
| `LabeledRow` | (`props`: { `children`: `ReactNode` ; `modified?`: `boolean` ; `title`: `string`  }) => `Element` |
| `SavingOverlay` | (`props`: { `errorMessage`: `undefined` \| `string` ; `isSaving`: `boolean` ; `resetLocalConfig`: () => `void` ; `saveLocalConfig`: () => `void`  }) => `Element` |

#### Defined in

[components/configuration/index.ts:15](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/components/configuration/index.ts#L15)

___

### essentialComponents

• **essentialComponents**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `Button` | (`props`: { `children`: `ReactNode` ; `className?`: `string` ; `disabled?`: `boolean` ; `dot?`: `boolean` ; `spinner?`: `boolean` ; `variant`: ``"white"`` \| ``"green"`` \| ``"red"`` \| ``"gray"`` \| ``"flat-blue"`` ; `onClick`: () => `void`  }) => `Element` |
| `LiveSwitch` | (`props`: { `isLive`: `boolean` ; `toggle`: (`v`: `boolean`) => `void`  }) => `Element` |
| `LogLine` | (`props`: { `text`: `string`  }) => `Element` |
| `NumericButton` | (`props`: { `children`: `ReactNode` ; `className?`: `string` ; `disabled?`: `boolean` ; `initialValue`: `number` ; `postfix?`: `string` ; `spinner?`: `boolean` ; `onClick`: (`value`: `number`) => `void`  }) => `Element` |
| `Ping` | (`props`: { `state`: `undefined` \| `boolean`  }) => `Element` |
| `PreviousValue` | (`props`: { `previousValue?`: `any`  }) => `Element` |
| `Spinner` | () => `Element` |
| `TextInput` | (`props`: { `disabled?`: `boolean` ; `postfix?`: `string` ; `small?`: `boolean` ; `value`: `string` ; `setValue`: (`v`: `string`) => `void`  }) => `Element` |
| `Toggle` | (`props`: { `className?`: `string` ; `value`: `string` ; `values`: `string`[] ; `setValue`: (`v`: `string`) => `void`  }) => `Element` |

#### Defined in

[components/essential/index.ts:11](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/components/essential/index.ts#L11)

___

### overviewComponents

• **overviewComponents**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `ActivityPlot` | () => `Element` |

#### Defined in

[components/overview/index.ts:3](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/components/overview/index.ts#L3)

___

### structuralComponents

• **structuralComponents**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `DisconnectedScreen` | (`props`: { `backendIntegrity`: `undefined` \| ``"cli is missing"`` \| ``"config is invalid"`` \| ``"pyra-core is not running"`` ; `loadInitialAppState`: () => `void` ; `startPyraCore`: () => `void`  }) => `Element` |
| `Header` | (`props`: { `activeTab`: `string` ; `tabs`: `string`[] ; `setActiveTab`: (`t`: `string`) => `void`  }) => `Element` |
| `MessageQueue` | () => `Element` |

#### Defined in

[components/structural/index.ts:5](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/components/structural/index.ts#L5)
