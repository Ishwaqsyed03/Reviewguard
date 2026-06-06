"use client";

import { type VariantProps } from "class-variance-authority";
import { Menu, Shield } from "lucide-react";
import { ReactNode } from "react";

import { cn } from "@/lib/utils";

import { Button, buttonVariants } from "../../ui/button";
import {
  Navbar as NavbarComponent,
  NavbarLeft,
  NavbarRight,
} from "../../ui/navbar";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "../../ui/sheet";

interface NavbarLink { text: string; href: string; }
interface NavbarActionProps {
  text: string; href: string;
  variant?: VariantProps<typeof buttonVariants>["variant"];
  icon?: ReactNode; iconRight?: ReactNode; isButton?: boolean;
}
interface NavbarProps {
  logo?: ReactNode; name?: string; homeUrl?: string;
  mobileLinks?: NavbarLink[]; actions?: NavbarActionProps[];
  showNavigation?: boolean; customNavigation?: ReactNode; className?: string;
}

export default function Navbar({
  logo = <Shield className="size-5 text-brand" />,
  name = "ReviewGuard",
  homeUrl = "/",
  mobileLinks = [
    { text: "Detect a Review", href: "#detect" },
    { text: "Recommendations", href: "#recommendations" },
    { text: "Timeline", href: "#timeline" },
    { text: "History", href: "#history" },
  ],
  actions = [
    { text: "How It Works", href: "#how-it-works", isButton: false },
    { text: "Detect a Review", href: "#detect", isButton: true, variant: "default" },
  ],
  className,
}: NavbarProps) {
  return (
    <header className={cn("sticky top-0 z-50 -mb-4 px-4 pb-4", className)}>
      <div className="fade-bottom bg-background/15 absolute left-0 h-24 w-full backdrop-blur-lg"></div>
      <div className="max-w-container relative mx-auto">
        <NavbarComponent>
          <NavbarLeft>
            <a href={homeUrl} className="flex items-center gap-2 text-xl font-bold">
              {logo}{name}
            </a>
            <nav className="hidden items-center gap-6 md:flex">
              {mobileLinks.map(l => (
                <a key={l.href} href={l.href} className="text-muted-foreground hover:text-foreground text-sm transition-colors">{l.text}</a>
              ))}
            </nav>
          </NavbarLeft>
          <NavbarRight>
            {actions.map((action) =>
              action.isButton ? (
                <Button key={action.text} variant={action.variant || "default"} asChild>
                  <a href={action.href}>{action.text}</a>
                </Button>
              ) : (
                <a key={action.text} href={action.href} className="hidden text-sm md:block">{action.text}</a>
              )
            )}
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="shrink-0 md:hidden">
                  <Menu className="size-5" />
                  <span className="sr-only">Toggle navigation menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="right">
                <SheetTitle className="sr-only">Navigation menu</SheetTitle>
                <nav className="grid gap-6 text-lg font-medium">
                  <a href={homeUrl} className="flex items-center gap-2 text-xl font-bold">{name}</a>
                  {mobileLinks.map((link) => (
                    <a key={link.href} href={link.href} className="text-muted-foreground hover:text-foreground">{link.text}</a>
                  ))}
                </nav>
              </SheetContent>
            </Sheet>
          </NavbarRight>
        </NavbarComponent>
      </div>
    </header>
  );
}
