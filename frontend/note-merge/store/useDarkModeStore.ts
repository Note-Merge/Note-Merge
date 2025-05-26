import {create} from "zustand";


type DarkModeStore ={
  isDarkMode: boolean;
  toggleDarkMode: () => void;
}

export const useDarkModeStore = create<DarkModeStore>((set) => ({
  isDarkMode: true,
  toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
}));