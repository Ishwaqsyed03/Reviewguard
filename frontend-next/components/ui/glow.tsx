import { cva, VariantProps } from "class-variance-authority";
import React from "react";

import { cn } from "@/lib/utils";

const glowVariants = cva("absolute w-full", {
  variants: {
    variant: {
      top: "top-0",
      above: "-top-[128px]",
      bottom: "bottom-0",
      below: "-bottom-[128px]",
      center: "top-[50%]",
    },
  },
  defaultVariants: {
    variant: "top",
  },
});

function Glow({
  className,
  variant,
  ...props
}: React.ComponentProps<"div"> & VariantProps<typeof glowVariants>) {
  return (
    <div
      data-slot="glow"
      className={cn(glowVariants({ variant }), className)}
      {...props}
    >
      <div
        className={cn(
          "from-brand-foreground/50 to-brand-foreground/0 absolute left-1/2 h-[320px] w-[90%] -translate-x-1/2 scale-[3] rounded-[50%] bg-radial from-10% to-60% opacity-20 sm:h-[720px] dark:opacity-100 filter blur-[24px] transition-all duration-500 group-hover:scale-[3.4] group-hover:opacity-40 pointer-events-none",
          variant === "center" && "-translate-y-1/2",
        )}
      />
      <div
        className={cn(
          "from-brand/30 to-brand-foreground/0 absolute left-1/2 h-[220px] w-[60%] -translate-x-1/2 scale-[2.8] rounded-[50%] bg-radial from-10% to-60% opacity-20 sm:h-[420px] dark:opacity-100 filter blur-[12px] transition-all duration-500 group-hover:scale-[3] group-hover:opacity-30 pointer-events-none",
          variant === "center" && "-translate-y-1/2",
        )}
      />
    </div>
  );
}

export default Glow;
