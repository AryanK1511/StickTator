export type User = {
    name?: string | null;
    email?: string | null;
    image?: string | null;
};

export type Machine = {
    id: string;
    _id?: string;
    name: string;
    status: "connected" | "disconnected";
    created_at: string;
    email: string;
    machine_name: string;
};

export type WebSocketMessage = {
    type: "device_connected" | "device_disconnected" | "machines_list" | "error";
    data?: Machine[] | { machine_id: string };
    machine_id?: string;
    message?: string;
};

export type TextDisplayProps = {
    transcript: string;
    isListening: boolean;
};

export type VoiceButtonProps = {
    isListening: boolean;
    toggleListening: () => void;
};
