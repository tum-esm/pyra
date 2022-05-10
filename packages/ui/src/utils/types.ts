namespace TYPES {
    export type configJSON = {
        [key: string]: {
            [key: string]:
                | string
                | number
                | boolean
                | number[]
                | {
                      [key: string]:
                          | [number, number, number]
                          | [number, number, number, number]
                          | boolean;
                  };
        };
    };
}

export default TYPES;
