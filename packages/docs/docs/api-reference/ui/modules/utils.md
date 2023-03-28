---
id: "utils"
title: "Module: utils"
sidebar_label: "utils"
sidebar_position: 0
custom_edit_url: null
---

## Variables

### fetchUtils

• **fetchUtils**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `backend` | { `archiveLogs`: () => `Promise`<`ChildProcess`\> ; `checkPyraCoreState`: () => `Promise`<`ChildProcess`\> ; `getConfig`: () => `Promise`<`ChildProcess`\> ; `pyraCliIsAvailable`: () => `Promise`<`ChildProcess`\> ; `startPyraCore`: () => `Promise`<`ChildProcess`\> ; `stopPyraCore`: () => `Promise`<`ChildProcess`\> ; `updateConfig`: (`newConfig`: [`partialConfig`](../namespaces/custom_types.customTypes.md#partialconfig)) => `Promise`<`ChildProcess`\> ; `writeToPLC`: (`command`: `string`[]) => `Promise`<`ChildProcess`\>  } |
| `backend.archiveLogs` | () => `Promise`<`ChildProcess`\> |
| `backend.checkPyraCoreState` | () => `Promise`<`ChildProcess`\> |
| `backend.getConfig` | () => `Promise`<`ChildProcess`\> |
| `backend.pyraCliIsAvailable` | () => `Promise`<`ChildProcess`\> |
| `backend.startPyraCore` | () => `Promise`<`ChildProcess`\> |
| `backend.stopPyraCore` | () => `Promise`<`ChildProcess`\> |
| `backend.updateConfig` | (`newConfig`: [`partialConfig`](../namespaces/custom_types.customTypes.md#partialconfig)) => `Promise`<`ChildProcess`\> |
| `backend.writeToPLC` | (`command`: `string`[]) => `Promise`<`ChildProcess`\> |
| `getFileContent` | (`filePath`: `string`) => `Promise`<`string`\> |
| `getProjectDirPath` | () => `Promise`<`string`\> |
| `initialAppState` | (`dispatch`: `any`, `setBackendIntegrity`: (`value`: `undefined` \| ``"cli is missing"`` \| ``"config is invalid"`` \| ``"pyra-core is not running"`` \| ``"valid"``) => `void`) => `Promise`<`void`\> |

#### Defined in

[utils/fetch-utils/index.ts:6](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/utils/fetch-utils/index.ts#L6)

___

### functionalUtils

• **functionalUtils**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `deepEqual` | (`a`: `any`, `b`: `any`) => `boolean` |
| `generateActivityHistories` | (`activityHistory`: [`activityHistory`](../namespaces/custom_types.customTypes.md#activityhistory), `measurementsAreRunning`: `boolean`, `errorIsPresent`: `boolean`) => { `core`: `ActivitySection`[] ; `error`: `ActivitySection`[] ; `measurements`: `ActivitySection`[]  } |
| `parseNumberTypes` | (`newConfig`: [`config`](../namespaces/custom_types.customTypes.md#config)) => [`config`](../namespaces/custom_types.customTypes.md#config) |
| `reduceLogLines` | (`logLines`: `string`[], `mode`: ``"3 iterations"`` \| ``"5 minutes"``) => `string`[] |

#### Defined in

[utils/functional-utils/index.ts:6](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/utils/functional-utils/index.ts#L6)

___

### reduxUtils

• **reduxUtils**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `activityActions` | `CaseReducerActions`<{ `set`: (`state`: [`reduxStateActivity`](../namespaces/custom_types.customTypes.md#reduxstateactivity), `action`: { `payload`: [`activityHistory`](../namespaces/custom_types.customTypes.md#activityhistory)  }) => `void`  }\> |
| `configActions` | `CaseReducerActions`<{ `resetLocal`: (`state`: [`reduxStateConfig`](../namespaces/custom_types.customTypes.md#reduxstateconfig)) => `void` ; `setConfigs`: (`state`: [`reduxStateConfig`](../namespaces/custom_types.customTypes.md#reduxstateconfig), `action`: { `payload`: `undefined` \| [`config`](../namespaces/custom_types.customTypes.md#config)  }) => `void` ; `setConfigsPartial`: (`state`: [`reduxStateConfig`](../namespaces/custom_types.customTypes.md#reduxstateconfig), `action`: { `payload`: [`partialConfig`](../namespaces/custom_types.customTypes.md#partialconfig)  }) => `void` ; `setErrorMessage`: (`state`: [`reduxStateConfig`](../namespaces/custom_types.customTypes.md#reduxstateconfig), `action`: { `payload`: `undefined` \| `string`  }) => `void` ; `setLocal`: (`state`: [`reduxStateConfig`](../namespaces/custom_types.customTypes.md#reduxstateconfig), `action`: { `payload`: `undefined` \| [`config`](../namespaces/custom_types.customTypes.md#config)  }) => `void` ; `setLocalPartial`: (`state`: [`reduxStateConfig`](../namespaces/custom_types.customTypes.md#reduxstateconfig), `action`: { `payload`: [`partialConfig`](../namespaces/custom_types.customTypes.md#partialconfig)  }) => `void`  }\> |
| `coreProcessActions` | `CaseReducerActions`<{ `set`: (`state`: [`reduxStateCoreProcess`](../namespaces/custom_types.customTypes.md#reduxstatecoreprocess), `action`: { `payload`: [`reduxStateCoreProcess`](../namespaces/custom_types.customTypes.md#reduxstatecoreprocess)  }) => `void`  }\> |
| `coreStateActions` | `CaseReducerActions`<{ `set`: (`state`: [`reduxStateCoreState`](../namespaces/custom_types.customTypes.md#reduxstatecorestate), `action`: { `payload`: [`coreState`](../namespaces/custom_types.customTypes.md#corestate)  }) => `void` ; `setPartial`: (`state`: [`reduxStateCoreState`](../namespaces/custom_types.customTypes.md#reduxstatecorestate), `action`: { `payload`: [`partialCoreState`](../namespaces/custom_types.customTypes.md#partialcorestate)  }) => `void`  }\> |
| `logsActions` | `CaseReducerActions`<{ `set`: (`state`: [`reduxStateLogs`](../namespaces/custom_types.customTypes.md#reduxstatelogs), `action`: { `payload`: `string`[]  }) => `void` ; `setFetchUpdates`: (`state`: [`reduxStateLogs`](../namespaces/custom_types.customTypes.md#reduxstatelogs), `action`: { `payload`: `boolean`  }) => `void` ; `setRenderedLogScope`: (`state`: [`reduxStateLogs`](../namespaces/custom_types.customTypes.md#reduxstatelogs), `action`: { `payload`: ``"3 iterations"`` \| ``"5 minutes"``  }) => `void`  }\> |
| `store` | `EnhancedStore`<`Object`, `AnyAction`, [`ThunkMiddleware`<`Object`, `AnyAction`, `undefined`\>]\> |
| `useTypedDispatch` | () => `ThunkDispatch`<`Object`, `undefined`, `AnyAction`\> & `Dispatch`<`AnyAction`\> |
| `useTypedSelector` | `TypedUseSelectorHook`<[`reduxState`](../namespaces/custom_types.customTypes.md#reduxstate)\> |

#### Defined in

[utils/redux-utils/index.ts:13](https://github.com/tum-esm/pyra/blob/8f435c2/packages/ui/src/utils/redux-utils/index.ts#L13)
