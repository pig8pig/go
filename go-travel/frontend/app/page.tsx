"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { useState } from "react";

export default function Home() {
  const [input, setInput] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // TODO: Connect to backend
    console.log("Planning trip:", input);
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-2xl space-y-12"
      >
        {/* Title */}
        <h1 className="text-8xl font-bold text-center tracking-tight">
          go.
        </h1>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Where do you want to go?"
            className="w-full px-6 py-4 text-lg border-2 border-black bg-white text-black placeholder:text-gray-400 focus:outline-none focus:ring-4 focus:ring-black/10 transition-all"
            autoFocus
          />
          <button
            type="submit"
            className="absolute right-4 top-1/2 -translate-y-1/2 p-2 hover:bg-black hover:text-white transition-colors"
            aria-label="Submit"
          >
            <ArrowRight size={24} />
          </button>
        </form>
      </motion.div>
    </main>
  );
}
