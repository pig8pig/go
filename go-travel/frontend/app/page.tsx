"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, MapPin, Calendar, Sparkles, Loader2, Star, ExternalLink } from "lucide-react";
import { useState } from "react";

type Step = "city" | "dates" | "vibe" | "results";

interface Place {
  name: string;
  search_query: string;
  category: string;
  why: string;
  place_id?: string;
  formatted_address?: string;
  lat?: number;
  lng?: number;
  rating?: number;
  user_ratings_total?: number;
  opening_hours?: boolean;
  price_level?: number;
  photo_url?: string;
}

interface TripData {
  city: string;
  startDate: string;
  endDate: string;
  vibe: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [step, setStep] = useState<Step>("city");
  const [tripData, setTripData] = useState<TripData>({
    city: "",
    startDate: "",
    endDate: "",
    vibe: "",
  });
  const [places, setPlaces] = useState<Place[]>([]);
  const [currentInput, setCurrentInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCitySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentInput.trim()) return;
    setTripData({ ...tripData, city: currentInput });
    setCurrentInput("");
    setStep("dates");
  };

  const handleDatesSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!tripData.startDate || !tripData.endDate) return;
    setStep("vibe");
  };

  const fetchPlaces = async (vibeValue: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          city: tripData.city,
          start_date: tripData.startDate,
          end_date: tripData.endDate,
          vibe: vibeValue,
        }),
      });
      
      if (!response.ok) {
        throw new Error("Failed to generate places");
      }
      
      const data = await response.json();
      setPlaces(data.places || []);
      setStep("results");
    } catch (err) {
      console.error("Error fetching places:", err);
      setError("Failed to load places. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVibeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const vibeValue = currentInput;
    setTripData({ ...tripData, vibe: vibeValue });
    setCurrentInput("");
    await fetchPlaces(vibeValue);
  };

  const skipVibe = async () => {
    await fetchPlaces("");
  };

  const resetFlow = () => {
    setStep("city");
    setTripData({ city: "", startDate: "", endDate: "", vibe: "" });
    setPlaces([]);
    setCurrentInput("");
    setError(null);
  };

  const getCategoryEmoji = (category: string) => {
    const emojis: Record<string, string> = {
      landmark: "🏛️",
      restaurant: "🍽️",
      museum: "🎨",
      nature: "🌳",
      nightlife: "🌙",
      shopping: "🛍️",
      cultural: "⛩️",
    };
    return emojis[category] || "📍";
  };

  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <AnimatePresence mode="wait">
        {/* Step 1: City */}
        {step === "city" && (
          <motion.div
            key="city"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="w-full max-w-2xl space-y-12"
          >
            <div className="space-y-4">
              <h1 className="text-8xl font-bold text-center tracking-tight">
                go.
              </h1>
              <p className="text-center text-gray-500 text-lg">
                Where do you want to go?
              </p>
            </div>

            <form onSubmit={handleCitySubmit} className="relative">
              <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                value={currentInput}
                onChange={(e) => setCurrentInput(e.target.value)}
                placeholder="Enter a city"
                className="w-full pl-12 pr-14 py-4 text-lg border-2 border-black bg-white text-black placeholder:text-gray-400 focus:outline-none focus:ring-4 focus:ring-black/10 transition-all"
                autoFocus
              />
              <button
                type="submit"
                className="absolute right-4 top-1/2 -translate-y-1/2 p-2 hover:bg-black hover:text-white transition-colors"
                aria-label="Next"
              >
                <ArrowRight size={24} />
              </button>
            </form>
          </motion.div>
        )}

        {/* Step 2: Dates */}
        {step === "dates" && (
          <motion.div
            key="dates"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="w-full max-w-2xl space-y-12"
          >
            <div className="space-y-4">
              <h1 className="text-8xl font-bold text-center tracking-tight">
                go.
              </h1>
              <p className="text-center text-2xl font-medium">
                {tripData.city}
              </p>
              <p className="text-center text-gray-500 text-lg">
                When are you traveling?
              </p>
            </div>

            <form onSubmit={handleDatesSubmit} className="space-y-4">
              <div className="relative">
                <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="date"
                  value={tripData.startDate}
                  onChange={(e) => setTripData({ ...tripData, startDate: e.target.value })}
                  className="w-full pl-12 pr-6 py-4 text-lg border-2 border-black bg-white text-black focus:outline-none focus:ring-4 focus:ring-black/10 transition-all"
                  autoFocus
                />
                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 text-sm">
                  Start
                </span>
              </div>

              <div className="relative">
                <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="date"
                  value={tripData.endDate}
                  onChange={(e) => setTripData({ ...tripData, endDate: e.target.value })}
                  min={tripData.startDate}
                  className="w-full pl-12 pr-6 py-4 text-lg border-2 border-black bg-white text-black focus:outline-none focus:ring-4 focus:ring-black/10 transition-all"
                />
                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 text-sm">
                  End
                </span>
              </div>

              <button
                type="submit"
                disabled={!tripData.startDate || !tripData.endDate}
                className="w-full py-4 text-lg font-medium border-2 border-black bg-black text-white hover:bg-white hover:text-black transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              >
                Continue
              </button>
            </form>
          </motion.div>
        )}

        {/* Step 3: Vibe */}
        {step === "vibe" && (
          <motion.div
            key="vibe"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="w-full max-w-2xl space-y-12"
          >
            <div className="space-y-4">
              <h1 className="text-8xl font-bold text-center tracking-tight">
                go.
              </h1>
              <p className="text-center text-2xl font-medium">
                {tripData.city}
              </p>
              <p className="text-center text-gray-500 text-lg">
                What&apos;s the vibe? <span className="text-gray-400">(optional)</span>
              </p>
            </div>

            <form onSubmit={handleVibeSubmit} className="space-y-4">
              <div className="relative">
                <Sparkles className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  placeholder="Romantic, adventure, foodie, budget..."
                  className="w-full pl-12 pr-6 py-4 text-lg border-2 border-black bg-white text-black placeholder:text-gray-400 focus:outline-none focus:ring-4 focus:ring-black/10 transition-all"
                  autoFocus
                />
              </div>

              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={skipVibe}
                  className="flex-1 py-4 text-lg font-medium border-2 border-black bg-white text-black hover:bg-gray-100 transition-colors"
                >
                  Skip
                </button>
                <button
                  type="submit"
                  className="flex-1 py-4 text-lg font-medium border-2 border-black bg-black text-white hover:bg-white hover:text-black transition-colors"
                >
                  Continue
                </button>
              </div>
            </form>
          </motion.div>
        )}

        {/* Loading State */}
        {isLoading && (
          <motion.div
            key="loading"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="w-full max-w-2xl flex flex-col items-center justify-center space-y-8"
          >
            <h1 className="text-8xl font-bold text-center tracking-tight">
              go.
            </h1>
            <div className="flex flex-col items-center space-y-4">
              <Loader2 className="w-12 h-12 animate-spin" />
              <p className="text-xl text-gray-500">Planning your trip...</p>
            </div>
          </motion.div>
        )}

        {/* Step 4: Results */}
        {step === "results" && !isLoading && (
          <motion.div
            key="results"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="w-full max-w-4xl space-y-8"
          >
            <div className="space-y-2">
              <h1 className="text-6xl font-bold tracking-tight">
                go. <span className="font-normal">{tripData.city}</span>
              </h1>
              <p className="text-gray-500 text-lg">
                {tripData.startDate} → {tripData.endDate}
                {tripData.vibe && <span className="ml-2">• {tripData.vibe}</span>}
              </p>
            </div>

            {error && (
              <div className="p-4 border-2 border-red-500 text-red-500">
                {error}
              </div>
            )}

            {/* Places from API */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold">Recommended Places</h2>
              
              <div className="grid gap-4">
                {places.length > 0 ? (
                  places.map((place, i) => (
                    <motion.div
                      key={place.place_id || i}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="group p-6 border-2 border-black hover:bg-black hover:text-white transition-colors cursor-pointer"
                      onClick={() => {
                        if (place.lat && place.lng) {
                          window.open(`https://www.google.com/maps/search/?api=1&query=${place.lat},${place.lng}`, "_blank");
                        }
                      }}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-2xl">{getCategoryEmoji(place.category)}</span>
                            <h3 className="text-xl font-bold">{place.name}</h3>
                          </div>
                          <p className="text-gray-500 group-hover:text-gray-300 mt-1">
                            {place.why}
                          </p>
                          {place.formatted_address && (
                            <p className="text-sm text-gray-400 group-hover:text-gray-400 mt-2">
                              {place.formatted_address}
                            </p>
                          )}
                          <div className="flex items-center gap-4 mt-2">
                            {place.rating && (
                              <span className="flex items-center gap-1 text-sm">
                                <Star size={14} className="fill-current" />
                                {place.rating} ({place.user_ratings_total?.toLocaleString()})
                              </span>
                            )}
                            {place.opening_hours !== undefined && (
                              <span className={`text-sm ${place.opening_hours ? "text-green-600 group-hover:text-green-400" : "text-red-500 group-hover:text-red-400"}`}>
                                {place.opening_hours ? "Open now" : "Closed"}
                              </span>
                            )}
                          </div>
                        </div>
                        <ExternalLink size={20} className="opacity-50 group-hover:opacity-100" />
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <p className="text-gray-500">No places found. Try a different city or vibe.</p>
                )}
              </div>
            </div>

            <button
              onClick={resetFlow}
              className="py-4 px-8 text-lg font-medium border-2 border-black bg-white text-black hover:bg-black hover:text-white transition-colors"
            >
              Start Over
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
