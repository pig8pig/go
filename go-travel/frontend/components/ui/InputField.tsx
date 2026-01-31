"use client";

import { motion } from "framer-motion";
import { ComponentProps } from "react";

interface InputFieldProps extends ComponentProps<"input"> {
  label?: string;
}

export default function InputField({ label, className = "", ...props }: InputFieldProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full"
    >
      {label && (
        <label className="block text-sm font-medium mb-2 uppercase tracking-wide">
          {label}
        </label>
      )}
      <input
        className={`w-full px-6 py-4 text-lg border-2 border-black bg-white text-black placeholder:text-gray-400 focus:outline-none focus:ring-4 focus:ring-black/10 transition-all ${className}`}
        {...props}
      />
    </motion.div>
  );
}
