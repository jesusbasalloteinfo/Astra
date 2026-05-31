/**
 * Represents access permissions for a specific user on a device.
 */
export interface DeviceAccess {
    /** The unique identifier of the user. */
    user_id: string;
    /** The role of the user (owner or guest). */
    role: "owner" | "guest";
}

/**
 * Represents a basic device in the system.
 */
export interface Device {
    /** Unique identifier for the device. */
    device_id: string;
    /** Human-readable name of the device. */
    name: string;
    /** The ID of the device owner. */
    owner: string;
    /** The date/time when the device was linked. */
    linked: string; 
    /** Whether the device is currently online. */
    is_online: boolean;
    /** List of users who have access to this device. */
    access_list: DeviceAccess[];
}

/**
 * Categorizes the various components/drivers attached to a device.
 */
export interface DeviceComponents {
    /** List of telescope/mount drivers. */
    telescope: string[];
    /** List of camera drivers. */
    camera: string[];
    /** List of focuser drivers. */
    focuser: string[];
    /** List of filter wheel drivers. */
    filter_wheel: string[];
    /** List of generic INDI drivers. */
    indi: string[];
}

/**
 * Extends the basic Device interface with component-specific information.
 */
export interface DeviceInfo extends Device {
    /** The hardware components associated with this device. */
    components: DeviceComponents;
}

/**
 * Data required to initiate a device pairing request.
 */
export interface PairingRequest{
    /** The PIN provided by the device for pairing. */
    pin: string
}

/**
 * Response received after a successful pairing request.
 */
export interface PairingResponse{
    /** The unique identifier assigned to the paired device. */
    device_id: string
}



// OPERATIONS

/**
 * Represents equatorial coordinates.
 */
interface Coordinates {
  /** Right Ascension. */
  ra: number;
  /** Declination. */
  dec: number;
}

/**
 * Represents horizontal coordinates.
 */
interface HorizontalCoordinates {
  /** Altitude. */
  alt: number;
  /** Azimuth. */
  az: number;
}

/**
 * Represents the current position of a telescope in multiple coordinate systems.
 */
export interface TelescopePosition {
  /** J2000 equatorial coordinates. */
  equatorial_j2000: Coordinates;
  /** Epoch of Date equatorial coordinates. */
  equatorial_eod: Coordinates;
  /** Horizontal (Alt/Az) coordinates. */
  horizontal: HorizontalCoordinates;
}


/**
 * Supported coordinate system types for telescope operations.
 */
export enum CoordinateTypes {
    /** Equatorial coordinates (J2000). */
    EQUATORIAL_J2000 = "EQUATORIAL_COORD",
    /** Equatorial coordinates (Epoch of Date). */
    EQUATORIAL_EOD = "EQUATORIAL_EOD_COORD",
    /** Horizontal coordinates (Alt/Az). */
    HORIZONTAL = "HORIZONTAL_COORD"
}

/**
 * Modes for telescope movement.
 * SLEW: Move to target.
 * TRACK: Move to and track target.
 * SYNC: Synchronize telescope position with target.
 */
export type SlewMode = "SLEW" | "TRACK" | "SYNC";

/**
 * Command structure for slewing or syncing the telescope.
 */
export interface SlewCommand {
    /** Target coordinates as [RA, Dec] or [Alt, Az]. */
    coord: [number, number]; 
    /** The coordinate system type used in the coord array. */
    input_type: CoordinateTypes;
    /** The movement mode to execute. */
    mode: SlewMode;
}
