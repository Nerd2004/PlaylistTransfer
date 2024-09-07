"use client";
import axios from "axios";
import { useEffect, useState, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2, Music, LogOut, Search, FileUp, FileDown } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Progress } from "@/components/ui/progres";

interface UserInfo {
  name: string;
  email: string;
  picture: string;
}

export default function Component() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [playlistLink, setPlaylistLink] = useState("");
  const [responseLink, setresponseLink] = useState("");
  const [isTransferring, setIsTransferring] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [isUserInfoOpen, setIsUserInfoOpen] = useState(false);
  const [transferProgress, setTransferProgress] = useState(0);
  const [transferStatus, setTransferStatus] = useState("");
  const [totalSongs, setTotalSongs] = useState(0);

  const handleSignIn = async () => {
    setIsAuthenticating(true);
    window.location.href = "https://playlisttransfer.site/login";
  };

  const handleSignOut = () => {
    setIsLoading(true);
    window.location.href = "https://playlisttransfer.site/logout";
    setPlaylistLink("");
    setUserInfo(null);
  };

  useEffect(() => {
    const checkAuth = async () => {
      setIsLoading(true);
      try {
        const response = await fetch("https://playlisttransfer.site/check", {
          method: "GET",
          credentials: "include",
        });
        if (response.ok) {
          const user = await response.json();
          setIsAuthenticated(true);
          setUserInfo({
            name: user.name,
            email: user.email,
            picture: user.picture,
          });
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error("Error checking authentication:", error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleTransfer = async () => {
    setIsTransferring(true);
    setresponseLink("");
    setTransferProgress(5);
    setTransferStatus("Initializing transfer...");

    const eventSource = new EventSource("https://playlisttransfer.site/logs");
    let percentageIncrement = 0;
    let totalSongs = 0;
    eventSource.onmessage = (event) => {
      const message = event.data;
      setTransferStatus(message);

      if (message.startsWith("Extracting Songs from Playlist")) {
        setTransferProgress(20);
      } else if (message.startsWith("Searching for")) {
        setTransferProgress(40);
      } else if (message.startsWith("PlaylistTransfer Found Total")) {
        setTransferProgress(60);
        const match = message.match(/PlaylistTransfer Found Total (\d+) songs/);
        if (match) {
          totalSongs = parseInt(match[1], 10);
          percentageIncrement = (1 / totalSongs) * 100;
          percentageIncrement = (percentageIncrement / 100) * 30;
          setTotalSongs(totalSongs);
        }
      } else if (message.startsWith("Creating the Playlist")) {
        setTransferProgress(65);
      } else if (message.startsWith("Playlist created successfully!")) {
        setTransferProgress(70);
      } else {
        setTransferProgress((prevProgress) => {
          const newProgress = prevProgress + percentageIncrement;
          return Math.min(newProgress, 100); // Ensure progress does not exceed 100%
        });
      }
    };

    eventSource.onerror = (error) => {
      console.error("EventSource error:", error);
    };

    try {
      const response = await fetch(
        "https://playlisttransfer.site/scrapeplaylist",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
          },
          credentials: "include",
          body: JSON.stringify({ playlistLink: playlistLink }), // Sending the link in the body
        }
      );

      if (response.ok) {
        const data = await response.json(); // Await the .json() method to parse the response
        setresponseLink(data.url);
        console.log(data);
      }
    } catch (error) {
      console.error("Error fetching Playlist from frontend:", error);
    } finally {
      // Ensure to close the EventSource after the operation completes
      eventSource.close();
    }
    setTransferProgress(100);
    setIsTransferring(false);
  };

  const handleViewPlaylist = () => {
    // Add logic to view the transferred playlist
    window.location.href = responseLink;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#000000] p-4 flex flex-col">
        <header className="w-full max-w-4xl mx-auto mb-8 flex justify-between items-center">
          <Skeleton className="h-8 w-40 bg-[#222222]" />
          <Skeleton className="h-10 w-10 rounded-full bg-[#222222]" />
        </header>
        <main className="flex-grow flex flex-col items-center justify-center space-y-8 w-full max-w-2xl mx-auto">
          <Skeleton className="h-12 w-3/4 bg-[#222222]" />
          <Skeleton className="h-6 w-1/2 bg-[#222222]" />
          <div className="w-full space-y-4">
            <Skeleton className="h-12 w-full bg-[#222222]" />
            <Skeleton className="h-12 w-full bg-[#222222]" />
          </div>
        </main>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#000000] p-4">
        <Card className="w-full max-w-md bg-[#111111] border-[#333333]">
          <CardHeader className="space-y-1">
            <div className="flex items-center justify-center mb-4">
              <Music className="h-12 w-12 text-[#50E3C2]" />
            </div>
            <CardTitle className="text-2xl font-bold text-center text-white">
              Welcome to Playlist Transfer
            </CardTitle>
            <CardDescription className="text-center text-gray-400">
              Sign in with Google to start transferring your playlists
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              onClick={handleSignIn}
              disabled={isAuthenticating}
              className="w-full bg-white hover:bg-gray-200 text-black font-semibold py-2 px-4 rounded transition-colors duration-300 flex items-center justify-center"
            >
              {isAuthenticating ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin text-black" />
                  Signing In...
                </>
              ) : (
                <>
                  <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                    <path fill="none" d="M1 1h22v22H1z" />
                  </svg>
                  Sign in with Google
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#000000] p-4">
      <header className="max-w-4xl mx-auto mb-8 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Music className="h-8 w-8 text-[#50E3C2]" />
          <h1 className="text-2xl font-bold text-white">Playlist Transfer</h1>
        </div>
        <div className="flex items-center space-x-4">
          <Popover open={isUserInfoOpen} onOpenChange={setIsUserInfoOpen}>
            <PopoverTrigger asChild>
              <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={userInfo?.picture} alt={userInfo?.name} />
                  <AvatarFallback>{userInfo?.name[0]}</AvatarFallback>
                </Avatar>
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80 bg-[#111111] border-[#333333] text-white">
              <div className="flex flex-col items-center space-y-2">
                <Avatar className="h-20 w-20">
                  <AvatarImage src={userInfo?.picture} alt={userInfo?.name} />
                  <AvatarFallback>{userInfo?.name[0]}</AvatarFallback>
                </Avatar>
                <h2 className="text-xl font-semibold">{userInfo?.name}</h2>
                <p className="text-sm text-gray-400">{userInfo?.email}</p>
              </div>
            </PopoverContent>
          </Popover>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleSignOut}
            className="text-gray-400 hover:text-white hover:bg-[#333333]"
          >
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </header>
      <Card className="max-w-md mx-auto bg-[#111111] border-[#333333]">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-center text-white">
            Transfer Spotify Playlist
          </CardTitle>
          <CardDescription className="text-center text-gray-400">
            Enter your Spotify playlist link to transfer
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            type="text"
            placeholder="https://open.spotify.com/playlist/..."
            value={playlistLink}
            onChange={(e) => setPlaylistLink(e.target.value)}
            className="w-full bg-[#222222] border-[#444444] text-white placeholder-gray-500 focus:border-[#50E3C2] transition-all duration-300 ease-in-out"
          />
          <Button
            onClick={handleTransfer}
            disabled={isTransferring || !playlistLink}
            className="w-full bg-[#50E3C2] hover:bg-[#3AC7A8] text-black font-semibold py-2 px-4 rounded transition-colors duration-300"
          >
            {isTransferring ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Transferring...
              </>
            ) : (
              "Transfer Playlist"
            )}
          </Button>
          {responseLink != "" && (
            <Button
              onClick={handleViewPlaylist}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded transition-colors duration-300"
            >
              View Playlist
            </Button>
          )}
          {isTransferring && (
            <div className="mt-4 space-y-4">
              <div className="flex flex-col items-center justify-center space-y-2">
                {transferProgress < 30 && (
                  <FileDown className="w-12 h-12 text-[#50E3C2] animate-bounce" />
                )}
                {transferProgress >= 30 && transferProgress < 65 && (
                  <Search className="w-12 h-12 text-[#50E3C2] animate-pulse" />
                )}
                {transferProgress >= 65 && (
                  <FileUp className="w-12 h-12 text-[#50E3C2] animate-pulse" />
                )}
                <span className="text-sm text-gray-300 text-center">
                  {transferStatus}
                </span>
              </div>
              <Progress
                value={transferProgress}
                className="w-full h-2 bg-[#222222]"
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
