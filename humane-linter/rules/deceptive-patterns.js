module.exports = [
  // Each pattern will be defined as an object with name, description, and regex
  // Example structure:
  // {
  //   name: "Pattern Name",
  //   description: "Description of why this pattern is deceptive",
  //   regex: /pattern to match/
  // }
  {
    name: "Infinite Scroll Pattern",
    description: "Implements infinite scrolling without clear stopping cues, prioritizing engagement over user autonomy",
    regex: /(new\s+IntersectionObserver|addEventListener\s*\(\s*['"]scroll['"]|infiniteScroll|loadMore|onScroll|scrollHandler|infinite-scroll|infinite_scroll)/
  }
];
