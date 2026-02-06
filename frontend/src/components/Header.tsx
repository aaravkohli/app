import { motion } from "framer-motion";
import { Shield, Github, Lock, CheckCircle2, Wifi, WifiOff, LogOut, User } from "lucide-react";
import { useState, useEffect } from "react";
import { apiService } from "@/lib/apiService.ts";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useNavigate } from "react-router-dom";

const Header = () => {
  const [isBackendConnected, setIsBackendConnected] = useState<boolean | null>(null);
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (error) {
      console.error("Failed to log out:", error);
    }
  };

  const getUserInitials = () => {
    if (currentUser?.displayName) {
      return currentUser.displayName
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    }
    return currentUser?.email?.[0]?.toUpperCase() || "U";
  };

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const connected = await apiService.healthCheck();
        setIsBackendConnected(connected);
      } catch {
        setIsBackendConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full px-4 md:px-8 py-4 flex items-center justify-between border-b border-border/30"
    >
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/20 rounded-xl blur-lg animate-glow-pulse" />
          <div className="relative p-2.5 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20">
            <Shield className="w-6 h-6 text-primary" />
          </div>
        </div>
        <div>
          <h1 className="text-lg font-semibold text-foreground">
            Prompt<span className="gradient-text">Guard</span>
          </h1>
          <p className="text-xs text-muted-foreground -mt-0.5">
            AI Security Gateway
          </p>
        </div>
      </div>

      {/* Center - Security Status (prominent) */}
      <div className="hidden md:flex items-center gap-3">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="flex items-center gap-3 px-4 py-2 rounded-full bg-safe/10 border border-safe/30 shadow-lg shadow-safe/10"
        >
          <div className="relative">
            <div className="absolute inset-0 bg-safe rounded-full blur-sm animate-pulse opacity-50" />
            <div className="relative w-2.5 h-2.5 rounded-full bg-safe" />
          </div>
          <div className="flex items-center gap-2">
            <Lock className="w-3.5 h-3.5 text-safe" />
            <span className="text-sm font-medium text-safe">Gateway Protected</span>
          </div>
          <CheckCircle2 className="w-4 h-4 text-safe" />
        </motion.div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Backend Connection Status */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all ${
            isBackendConnected === null
              ? "bg-muted/30 border-border/50"
              : isBackendConnected
              ? "bg-green-500/10 border-green-500/30"
              : "bg-red-500/10 border-red-500/30"
          }`}
          title={
            isBackendConnected === null
              ? "Checking connection..."
              : isBackendConnected
              ? "Backend connected"
              : "Backend disconnected"
          }
        >
          {isBackendConnected === null ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                <Wifi className="w-3.5 h-3.5 text-muted-foreground" />
              </motion.div>
              <span className="text-xs font-medium text-muted-foreground hidden sm:inline">
                Checking...
              </span>
            </>
          ) : isBackendConnected ? (
            <>
              <div className="relative">
                <div className="absolute inset-0 bg-green-500 rounded-full blur-sm animate-pulse opacity-50" />
                <div className="relative w-2 h-2 rounded-full bg-green-500" />
              </div>
              <Wifi className="w-3.5 h-3.5 text-green-600" />
              <span className="text-xs font-medium text-green-600 hidden sm:inline">
                Connected
              </span>
            </>
          ) : (
            <>
              <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              <WifiOff className="w-3.5 h-3.5 text-red-600" />
              <span className="text-xs font-medium text-red-600 hidden sm:inline">
                Offline
              </span>
            </>
          )}
        </motion.div>

        {/* Mobile security indicator */}
        <div className="md:hidden flex items-center gap-2 px-3 py-1.5 rounded-full bg-safe/10 border border-safe/20">
          <div className="w-2 h-2 rounded-full bg-safe animate-pulse" />
          <span className="text-xs font-medium text-safe">Protected</span>
        </div>

        {/* User Menu */}
        {currentUser && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                <Avatar className="h-9 w-9">
                  <AvatarImage src={currentUser.photoURL || undefined} alt={currentUser.displayName || "User"} />
                  <AvatarFallback className="bg-primary/10 text-primary">
                    {getUserInitials()}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {currentUser.displayName || "User"}
                  </p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {currentUser.email}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
        
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 rounded-lg hover:bg-muted/50 text-muted-foreground hover:text-foreground transition-colors"
        >
          <Github className="w-5 h-5" />
        </a>
      </div>
    </motion.header>
  );
};

export default Header;
