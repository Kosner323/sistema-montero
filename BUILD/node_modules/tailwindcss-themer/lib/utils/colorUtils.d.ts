/**
 * @param value - a color represented as a string (hex, rgb, rgba, hsl, hsla, etc)
 * @return the color represented as its rgb values with alpha channel stripped
 */
export declare const toRgb: (value: string) => string;
/**
 * @param value - a color represented as a string (hex, rgb, rgba, hsl, hsla, etc)
 * @return the alpha channel of the color
 */
export declare const getAlpha: (value: string | number) => number;
/**
 * @param value - the value to test if it is a valid color string
 * @return whether the value passed in is a valid color string
 */
export declare const isColor: (value: string | number) => boolean;
