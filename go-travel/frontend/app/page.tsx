"use client";

import { motion, AnimatePresence } from "framer-motion";
import { 
  ArrowRight, 
  MapPin, 
  Calendar, 
  Sparkles, 
  Loader2, 
  Star, 
  Clock,
  Navigation,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  MapPinned
} from "lucide-react";
import { useState } from "react";

type Step = "city" | "dates" | "vibe" | "results";

// ========== TYPE DEFINITIONS (matching backend response_models.py) ==========

interface Coordinates {
  lat: number;
  lng: number;
}

interface TimeSlot {
  arrival: string;
  departure: string;
  duration_minutes: number;
}

interface ItineraryPlace {
  id: string;
  name: string;
  category: string;
  coordinates: Coordinates;
  time: TimeSlot;
  score: number;
  why: string;
  address?: string;
  photo_url?: string;
  rating?: number;
  review_count?: number;
}

interface DaySummary {
  num_places: number;
  total_score: number;
  travel_time_minutes: number;
  visit_time_minutes: number;
  total_time_minutes: number;
  start_time: string | null;
  end_time: string | null;
}

interface DayPlan {
  day_number: number;
  date: string | null;
  places: ItineraryPlace[];
  summary: DaySummary;
}

interface TripSummary {
  city: string;
  num_days: number;
  start_date: string | null;
  end_date: string | null;
  total_places: number;
  total_score: number;
  places_dropped: number;
  vibe: string | null;
}

interface ItineraryResponse {
  success: boolean;
  error: string | null;
  trip: TripSummary;
  days: DayPlan[];
  hotel: Coordinates | null;
}

interface TripData {
  city: string;
  startDate: string;
  endDate: string;
  vibe: string;
}

// ========== CONSTANTS ==========

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const CATEGORY_CONFIG: Record<string, { emoji: string; color: string }> = {
  landmark: { emoji: "🏛️", color: "border-l-amber-500" },
  restaurant: { emoji: "🍽️", color: "border-l-red-500" },
  museum: { emoji: "🎨", color: "border-l-purple-500" },
  nature: { emoji: "🌳", color: "border-l-green-500" },
  nightlife: { emoji: "🌙", color: "border-l-indigo-500" },
  shopping: { emoji: "🛍️", color: "border-l-pink-500" },
  cultural: { emoji: "⛩️", color: "border-l-orange-500" },
  cafe: { emoji: "☕", color: "border-l-yellow-600" },
  other: { emoji: "📍", color: "border-l-gray-500" },
};

// ========== HELPER FUNCTIONS ==========

const getCategoryConfig = (category: string) => {
  return CATEGORY_CONFIG[category.toLowerCase()] || CATEGORY_CONFIG.other;
};

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return "";
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("en-US", { 
    weekday: "short", 
    month: "short", 
    day: "numeric" 
  });
};

const formatDuration = (minutes: number) => {
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
};

// ========== COMPONENTS ==========

function PlaceCard({ place, index }: { place: ItineraryPlace; index: number }) {
  const config = getCategoryConfig(place.category);
  
  const openInMaps = () => {
    const { lat, lng } = place.coordinates;
    window.open(
      `https://www.google.com/maps/search/?api=1&query=${lat},${lng}&query_place_id=${place.id}`,
      "_blank"
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`relative pl-4 border-l-4 ${config.color}`}
    >
      {/* Time badge */}
      <div className="absolute -left-[52px] top-0 w-[44px] text-right">
        <span className="text-sm font-mono text-gray-500">
          {place.time.arrival.replace(" AM", "a").replace(" PM", "p")}
        </span>
      </div>

      <div 
        onClick={openInMaps}
        className="group p-4 bg-white border-2 border-gray-200 hover:border-black hover:shadow-lg transition-all cursor-pointer"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="flex items-center gap-2">
              <span className="text-xl flex-shrink-0">{config.emoji}</span>
              <h4 className="font-bold text-lg truncate">{place.name}</h4>
            </div>

            {/* Why */}
            <p className="text-gray-600 text-sm mt-1 line-clamp-2">{place.why}</p>

            {/* Meta row */}
            <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-gray-500">
              {/* Duration */}
              <span className="flex items-center gap-1">
                <Clock size={14} />
                {formatDuration(place.time.duration_minutes)}
              </span>

              {/* Rating */}
              {place.rating && (
                <span className="flex items-center gap-1">
                  <Star size={14} className="fill-yellow-400 text-yellow-400" />
                  {place.rating.toFixed(1)}
                  {place.review_count && (
                    <span className="text-gray-400">
                      ({place.review_count.toLocaleString()})
                    </span>
                  )}
                </span>
              )}

              {/* Score badge */}
              <span className="px-2 py-0.5 bg-black text-white text-xs font-medium rounded">
                {Math.round(place.score)}
              </span>
            </div>

            {/* Address */}
            {place.address && (
              <p className="text-xs text-gray-400 mt-2 truncate">
                {place.address}
              </p>
            )}
          </div>

          {/* Map icon */}
          <div className="flex-shrink-0 p-2 text-gray-400 group-hover:text-black transition-colors">
            <Navigation size={20} />
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function DayCard({ day, isExpanded, onToggle }: { 
  day: DayPlan; 
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const hasPlaces = day.places.length > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-2 border-black"
    >
      {/* Day Header */}
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between bg-black text-white hover:bg-gray-900 transition-colors"
      >
        <div className="flex items-center gap-4">
          <span className="text-2xl font-bold">Day {day.day_number}</span>
          {day.date && (
            <span className="text-gray-400">{formatDate(day.date)}</span>
          )}
        </div>

        <div className="flex items-center gap-4">
          {hasPlaces ? (
            <>
              <span className="text-sm text-gray-400">
                {day.summary.num_places} places • {formatDuration(day.summary.total_time_minutes)}
              </span>
              {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </>
          ) : (
            <span className="text-sm text-gray-500">Free day</span>
          )}
        </div>
      </button>

      {/* Day Content */}
      <AnimatePresence>
        {isExpanded && hasPlaces && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-6 pl-16 space-y-4 bg-gray-50">
              {/* Time range */}
              <div className="flex items-center gap-2 text-sm text-gray-500 -ml-12">
                <Clock size={16} />
                <span>
                  {day.summary.start_time} – {day.summary.end_time}
                </span>
                <span className="text-gray-400">
                  ({formatDuration(day.summary.visit_time_minutes)} visiting, {formatDuration(day.summary.travel_time_minutes)} traveling)
                </span>
              </div>

              {/* Places */}
              <div className="space-y-3">
                {day.places.map((place, i) => (
                  <PlaceCard key={place.id || i} place={place} index={i} />
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function TripHeader({ trip }: { trip: TripSummary }) {
  return (
    <div className="space-y-2">
      <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
        go. <span className="font-normal">{trip.city}</span>
      </h1>
      
      <div className="flex flex-wrap items-center gap-3 text-gray-500">
        {trip.start_date && trip.end_date && (
          <span className="flex items-center gap-1">
            <Calendar size={16} />
            {formatDate(trip.start_date)} → {formatDate(trip.end_date)}
          </span>
        )}
        
        {trip.vibe && (
          <span className="flex items-center gap-1">
            <Sparkles size={16} />
            {trip.vibe}
          </span>
        )}
      </div>

      {/* Stats bar */}
      <div className="flex flex-wrap gap-4 pt-2">
        <div className="px-3 py-1 bg-black text-white text-sm">
          {trip.num_days} {trip.num_days === 1 ? "day" : "days"}
        </div>
        <div className="px-3 py-1 bg-gray-100 text-sm">
          {trip.total_places} places
        </div>
        {trip.places_dropped > 0 && (
          <div className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm">
            {trip.places_dropped} couldn&apos;t fit
          </div>
        )}
      </div>
    </div>
  );
}

// ========== MAIN COMPONENT ==========

export default function Home() {
  const [step, setStep] = useState<Step>("city");
  const [tripData, setTripData] = useState<TripData>({
    city: "",
    startDate: "",
    endDate: "",
    vibe: "",
  });
  const [itinerary, setItinerary] = useState<ItineraryResponse | null>(null);
  const [currentInput, setCurrentInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([1]));

  const toggleDay = (dayNum: number) => {
    setExpandedDays(prev => {
      const next = new Set(prev);
      if (next.has(dayNum)) {
        next.delete(dayNum);
      } else {
        next.add(dayNum);
      }
      return next;
    });
  };

  const expandAllDays = () => {
    if (itinerary) {
      setExpandedDays(new Set(itinerary.days.map(d => d.day_number)));
    }
  };

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

  const fetchItinerary = async (vibeValue: string) => {
    setIsLoading(true);
    setError(null);
    setStep("results");
    
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
        throw new Error("Failed to generate itinerary");
      }
      
      const data: ItineraryResponse = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || "Unknown error occurred");
      }
      
      setItinerary(data);
      // Expand first day with places
      const firstDayWithPlaces = data.days.find(d => d.places.length > 0);
      if (firstDayWithPlaces) {
        setExpandedDays(new Set([firstDayWithPlaces.day_number]));
      }
    } catch (err) {
      console.error("Error fetching itinerary:", err);
      setError(err instanceof Error ? err.message : "Failed to load itinerary. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVibeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const vibeValue = currentInput;
    setTripData({ ...tripData, vibe: vibeValue });
    setCurrentInput("");
    await fetchItinerary(vibeValue);
  };

  const skipVibe = async () => {
    await fetchItinerary("");
  };

  const resetFlow = () => {
    setStep("city");
    setTripData({ city: "", startDate: "", endDate: "", vibe: "" });
    setItinerary(null);
    setCurrentInput("");
    setError(null);
    setExpandedDays(new Set([1]));
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
        {step === "vibe" && !isLoading && (
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
                  go.
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
              <p className="text-xl text-gray-500">Planning your perfect trip...</p>
              <p className="text-sm text-gray-400">
                Finding places • Checking weather • Optimizing routes
              </p>
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
            className="w-full max-w-4xl space-y-6 pb-12"
          >
            {/* Error State */}
            {error && (
              <div className="p-6 border-2 border-red-500 bg-red-50 space-y-4">
                <p className="text-red-600 font-medium">{error}</p>
                <button
                  onClick={resetFlow}
                  className="flex items-center gap-2 text-red-600 hover:text-red-800"
                >
                  <RotateCcw size={16} />
                  Try again
                </button>
              </div>
            )}

            {/* Itinerary */}
            {itinerary && (
              <>
                {/* Header */}
                <TripHeader trip={itinerary.trip} />

                {/* Action buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={expandAllDays}
                    className="flex items-center gap-2 px-4 py-2 text-sm border-2 border-gray-300 hover:border-black transition-colors"
                  >
                    <ChevronDown size={16} />
                    Expand all
                  </button>
                  {itinerary.hotel && (
                    <button
                      onClick={() => {
                        window.open(
                          `https://www.google.com/maps/search/?api=1&query=${itinerary.hotel!.lat},${itinerary.hotel!.lng}`,
                          "_blank"
                        );
                      }}
                      className="flex items-center gap-2 px-4 py-2 text-sm border-2 border-gray-300 hover:border-black transition-colors"
                    >
                      <MapPinned size={16} />
                      View hotel area
                    </button>
                  )}
                </div>

                {/* Days */}
                <div className="space-y-4">
                  {itinerary.days.map((day) => (
                    <DayCard
                      key={day.day_number}
                      day={day}
                      isExpanded={expandedDays.has(day.day_number)}
                      onToggle={() => toggleDay(day.day_number)}
                    />
                  ))}
                </div>

                {/* Footer */}
                <div className="pt-4 border-t border-gray-200">
                  <button
                    onClick={resetFlow}
                    className="flex items-center gap-2 py-3 px-6 text-lg font-medium border-2 border-black bg-white text-black hover:bg-black hover:text-white transition-colors"
                  >
                    <RotateCcw size={20} />
                    Plan another trip
                  </button>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
