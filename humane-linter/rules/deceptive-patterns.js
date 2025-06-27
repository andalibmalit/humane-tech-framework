const fs = require('fs');

function analyzeInfiniteScroll(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasStoppingMechanism = {
      hasLoadMoreButton: /(loadMore|load_more|load-more|LoadMore|Load More)/.test(context),
      hasPagination: /(pagination|pageSize|totalPages|currentPage)/.test(context),
      hasEndIndicator: /(endOfContent|noMoreContent|isLastPage|hasMore)/.test(context),
      hasScrollLimit: /(scrollLimit|maxScroll|scrollThreshold)/.test(context),
      hasUserControl: /(button|click|onClick|handleClick|userControl)/.test(context)
    };

    return {
      hasStoppingMechanism: Object.values(hasStoppingMechanism).some(v => v),
      details: hasStoppingMechanism
    };
  } catch (error) {
    return {
      hasStoppingMechanism: false,
      details: { error: error.message }
    };
  }
}

function analyzeAccountDeletion(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasDeletionMechanism = {
      hasDirectLink: /(deleteAccount|delete_account|delete-account|DeleteAccount|Delete Account|closeAccount|close_account|close-account|CloseAccount|Close Account)/.test(context),
      hasConfirmation: /(confirm|confirmation|verify|verification|are you sure).*(delete|close|remove).*(account|profile)/.test(context),
      hasEasyAccess: /(settings|account|profile|preferences).*(delete|close|remove).*(account|profile)/.test(context),
      hasClearInstructions: /(instructions|guide|how to|steps).*(delete|close|remove).*(account|profile)/.test(context),
      hasDataInfo: /(data|information|content|files|history).*(delete|close|remove).*(account|profile)/.test(context)
    };

    return {
      hasDeletionMechanism: Object.values(hasDeletionMechanism).some(v => v),
      details: hasDeletionMechanism
    };
  } catch (error) {
    return {
      hasDeletionMechanism: false,
      details: { error: error.message }
    };
  }
}

function analyzeHiddenCosts(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasTransparentPricing = {
      hasClearPricing: /(price|cost|fee|charge|total|amount).*(display|show|visible|clear)/.test(context),
      hasNoHiddenFees: /(hidden|additional|extra|surprise|unexpected).*(fee|cost|charge)/.test(context),
      hasUpfrontTotal: /(total|final|complete).*(price|cost|amount)/.test(context),
      hasTaxInfo: /(tax|vat|gst|duty).*(included|excluded|calculated)/.test(context),
      hasShippingInfo: /(shipping|delivery|handling).*(cost|fee|free)/.test(context)
    };

    return {
      hasTransparentPricing: Object.values(hasTransparentPricing).some(v => v),
      details: hasTransparentPricing
    };
  } catch (error) {
    return {
      hasTransparentPricing: false,
      details: { error: error.message }
    };
  }
}

function analyzeForcedContinuity(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasEasyCancellation = {
      hasCancelOption: /(cancel|cancellation|stop|end|terminate)/.test(context),
      hasNoAutoRenew: /(auto.*renew|automatic.*billing|recurring.*charge)/.test(context),
      hasClearTerms: /(terms|conditions|agreement).*(clear|visible|readable)/.test(context),
      hasEasyAccess: /(settings|account|billing).*(cancel|stop)/.test(context),
      hasNoPenalty: /(penalty|fee|charge).*(cancel|stop)/.test(context)
    };

    return {
      hasEasyCancellation: Object.values(hasEasyCancellation).some(v => v),
      details: hasEasyCancellation
    };
  } catch (error) {
    return {
      hasEasyCancellation: false,
      details: { error: error.message }
    };
  }
}

function analyzeRoachMotel(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasEasyExit = {
      hasLogout: /(logout|sign.*out|log.*out)/.test(context),
      hasDeleteOption: /(delete|remove|close).*(account|profile)/.test(context),
      hasUnsubscribe: /(unsubscribe|opt.*out|remove.*subscription)/.test(context),
      hasClearNavigation: /(menu|navigation|header).*(logout|exit)/.test(context),
      hasNoTraps: /(trap|prevent|block).*(logout|exit|leave)/.test(context)
    };

    return {
      hasEasyExit: Object.values(hasEasyExit).some(v => v),
      details: hasEasyExit
    };
  } catch (error) {
    return {
      hasEasyExit: false,
      details: { error: error.message }
    };
  }
}

function analyzePrivacyZuckering(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasPrivacyProtection = {
      hasOptIn: /(opt.*in|consent|permission).*(explicit|clear)/.test(context),
      hasNoDefaultSharing: /(share|public|visible).*(default|automatic)/.test(context),
      hasPrivacySettings: /(privacy|settings).*(control|manage)/.test(context),
      hasDataControl: /(data|information).*(control|manage|delete)/.test(context),
      hasTransparentSharing: /(share|publish).*(clear|visible|obvious)/.test(context)
    };

    return {
      hasPrivacyProtection: Object.values(hasPrivacyProtection).some(v => v),
      details: hasPrivacyProtection
    };
  } catch (error) {
    return {
      hasPrivacyProtection: false,
      details: { error: error.message }
    };
  }
}

function analyzeBaitAndSwitch(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasConsistentOffering = {
      hasClearTerms: /(terms|conditions|offer).*(clear|consistent)/.test(context),
      hasNoSurprises: /(surprise|unexpected|change).*(price|offer|service)/.test(context),
      hasTransparentPricing: /(price|cost).*(transparent|clear|honest)/.test(context),
      hasConsistentUI: /(interface|ui|design).*(consistent|clear)/.test(context),
      hasNoHiddenChanges: /(hidden|secret|obscure).*(change|modification)/.test(context)
    };

    return {
      hasConsistentOffering: Object.values(hasConsistentOffering).some(v => v),
      details: hasConsistentOffering
    };
  } catch (error) {
    return {
      hasConsistentOffering: false,
      details: { error: error.message }
    };
  }
}

function analyzeConfirmshaming(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasNeutralLanguage = {
      hasNeutralButtons: /(button|action).*(neutral|positive|clear)/.test(context),
      hasNoGuilt: /(guilt|shame|embarrassment|disappointment)/.test(context),
      hasRespectfulDecline: /(decline|no|cancel).*(respectful|polite)/.test(context),
      hasClearChoices: /(choice|option).*(clear|obvious)/.test(context),
      hasNoManipulation: /(manipulate|pressure|force).*(user|choice)/.test(context)
    };

    return {
      hasNeutralLanguage: Object.values(hasNeutralLanguage).some(v => v),
      details: hasNeutralLanguage
    };
  } catch (error) {
    return {
      hasNeutralLanguage: false,
      details: { error: error.message }
    };
  }
}

function analyzeDisguisedAds(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasClearAdvertising = {
      hasAdLabel: /(advertisement|ad|sponsored|promoted).*(label|marker)/.test(context),
      hasClearDisclosure: /(disclosure|disclose|reveal).*(ad|sponsored)/.test(context),
      hasNoDeception: /(deceive|mislead|trick).*(ad|content)/.test(context),
      hasVisualSeparation: /(separate|distinguish).*(ad|content)/.test(context),
      hasTransparentSponsorship: /(sponsor|partner).*(clear|visible)/.test(context)
    };

    return {
      hasClearAdvertising: Object.values(hasClearAdvertising).some(v => v),
      details: hasClearAdvertising
    };
  } catch (error) {
    return {
      hasClearAdvertising: false,
      details: { error: error.message }
    };
  }
}

function analyzeMisdirection(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasClearFocus = {
      hasClearCTAs: /(button|action|click).*(clear|obvious|prominent)/.test(context),
      hasNoDistractions: /(distract|divert|mislead).*(attention|focus)/.test(context),
      hasLogicalFlow: /(flow|navigation|path).*(logical|clear)/.test(context),
      hasConsistentUI: /(interface|design).*(consistent|predictable)/.test(context),
      hasNoConfusion: /(confuse|mislead|trick).*(user|interface)/.test(context)
    };

    return {
      hasClearFocus: Object.values(hasClearFocus).some(v => v),
      details: hasClearFocus
    };
  } catch (error) {
    return {
      hasClearFocus: false,
      details: { error: error.message }
    };
  }
}

function analyzeScarcityUrgency(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasHonestUrgency = {
      hasRealScarcity: /(limited|scarcity|urgency).*(real|genuine|authentic)/.test(context),
      hasNoFakeCountdown: /(countdown|timer).*(fake|artificial|manipulative)/.test(context),
      hasTransparentStock: /(stock|inventory).*(transparent|honest)/.test(context),
      hasNoPressure: /(pressure|rush|hurry).*(artificial|fake)/.test(context),
      hasClearDeadlines: /(deadline|expiry).*(clear|honest)/.test(context)
    };

    return {
      hasHonestUrgency: Object.values(hasHonestUrgency).some(v => v),
      details: hasHonestUrgency
    };
  } catch (error) {
    return {
      hasHonestUrgency: false,
      details: { error: error.message }
    };
  }
}

function analyzeTrickQuestions(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasClearQuestions = {
      hasSimpleLanguage: /(question|text).*(simple|clear|understandable)/.test(context),
      hasNoDoubleNegatives: /(not.*not|double.*negative)/.test(context),
      hasClearOptions: /(option|choice).*(clear|obvious)/.test(context),
      hasNoAmbiguity: /(ambiguous|unclear|confusing).*(question|text)/.test(context),
      hasLogicalFlow: /(flow|sequence).*(logical|clear)/.test(context)
    };

    return {
      hasClearQuestions: Object.values(hasClearQuestions).some(v => v),
      details: hasClearQuestions
    };
  } catch (error) {
    return {
      hasClearQuestions: false,
      details: { error: error.message }
    };
  }
}

function analyzePreselectedOptions(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasNeutralDefaults = {
      hasNoPreselection: /(preselected|default|checked).*(false|none)/.test(context),
      hasOptInDefaults: /(default|preselected).*(opt.*in|consent)/.test(context),
      hasClearChoices: /(choice|option).*(clear|obvious)/.test(context),
      hasNoManipulation: /(manipulate|trick|deceive).*(default|preselected)/.test(context),
      hasUserControl: /(user|control).*(choice|option)/.test(context)
    };

    return {
      hasNeutralDefaults: Object.values(hasNeutralDefaults).some(v => v),
      details: hasNeutralDefaults
    };
  } catch (error) {
    return {
      hasNeutralDefaults: false,
      details: { error: error.message }
    };
  }
}

function analyzeFriendSpam(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasRespectfulSharing = {
      hasExplicitConsent: /(consent|permission).*(explicit|clear)/.test(context),
      hasNoAutoInvite: /(invite|share).*(automatic|without.*permission)/.test(context),
      hasClearPurpose: /(purpose|reason).*(clear|obvious)/.test(context),
      hasOptOut: /(opt.*out|unsubscribe|stop).*(invite|share)/.test(context),
      hasNoDeception: /(deceive|trick|mislead).*(friend|contact)/.test(context)
    };

    return {
      hasRespectfulSharing: Object.values(hasRespectfulSharing).some(v => v),
      details: hasRespectfulSharing
    };
  } catch (error) {
    return {
      hasRespectfulSharing: false,
      details: { error: error.message }
    };
  }
}

function analyzeFakeSocialProof(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasAuthenticSocialProof = {
      hasRealReviews: /(review|testimonial).*(real|authentic|verified)/.test(context),
      hasNoFakeNumbers: /(number|count|statistic).*(fake|artificial|manipulated)/.test(context),
      hasTransparentMetrics: /(metric|statistic).*(transparent|honest)/.test(context),
      hasVerifiedUsers: /(user|reviewer).*(verified|authentic)/.test(context),
      hasNoDeception: /(deceive|fake|artificial).*(social|proof)/.test(context)
    };

    return {
      hasAuthenticSocialProof: Object.values(hasAuthenticSocialProof).some(v => v),
      details: hasAuthenticSocialProof
    };
  } catch (error) {
    return {
      hasAuthenticSocialProof: false,
      details: { error: error.message }
    };
  }
}

function analyzeObscuredUnsubscribe(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split(/\r?\n/);
    const startLine = Math.max(0, lineNumber - 10);
    const endLine = Math.min(lines.length, lineNumber + 20);
    const context = lines.slice(startLine, endLine).join('\n');

    const hasEasyUnsubscribe = {
      hasVisibleUnsubscribe: /(unsubscribe|opt.*out).*(visible|clear|obvious)/.test(context),
      hasOneClickUnsubscribe: /(unsubscribe|opt.*out).*(one.*click|simple)/.test(context),
      hasNoHiding: /(hide|obscure|conceal).*(unsubscribe|opt.*out)/.test(context),
      hasClearProcess: /(process|steps).*(clear|simple)/.test(context),
      hasNoTraps: /(trap|prevent|block).*(unsubscribe|opt.*out)/.test(context)
    };

    return {
      hasEasyUnsubscribe: Object.values(hasEasyUnsubscribe).some(v => v),
      details: hasEasyUnsubscribe
    };
  } catch (error) {
    return {
      hasEasyUnsubscribe: false,
      details: { error: error.message }
    };
  }
}

function analyzeMissingAccountDeletion(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    const isAccountRelated = /(settings|account|profile|preferences|user)/i.test(filePath);
    if (!isAccountRelated) return null;

    const hasAccountManagement = /(settings|account|profile|preferences|user)/i.test(content);
    if (!hasAccountManagement) return null;

    const hasNoDeletion = !/(delete|remove|terminate|close|deactivate).*(account|profile|user)/i.test(content);
    
    return {
      hasNoDeletion,
      details: {
        isAccountRelated,
        hasAccountManagement,
        hasNoDeletion
      }
    };
  } catch (error) {
    return null;
  }
}

module.exports = [
  {
    name: "Infinite Scroll Pattern",
    description: "Implements infinite scrolling without clear stopping cues, prioritizing engagement over user autonomy",
    regex: /(new\s+IntersectionObserver|addEventListener\s*\(\s*['"]scroll['"]|infiniteScroll|loadMore|onScroll|scrollHandler|infinite-scroll|infinite_scroll)/,
    analyze: analyzeInfiniteScroll
  },
  {
    name: "Account Deletion Accessibility",
    description: "Makes it difficult for users to delete their account, hiding or complicating the process",
    regex: /(delete|remove|terminate|close|deactivate).*(account|profile|user).*(settings|preferences|profile|account)/i,
    analyze: analyzeAccountDeletion
  },
  {
    name: "Hidden Costs",
    description: "Hides additional fees, taxes, or charges until after user commitment",
    regex: /(hidden|additional|extra|surprise|unexpected).*(fee|cost|charge|price|amount)/i,
    analyze: analyzeHiddenCosts
  },
  {
    name: "Forced Continuity",
    description: "Makes it difficult to cancel subscriptions or recurring payments",
    regex: /(subscription|recurring|auto.*renew|billing).*(cancel|stop|end|terminate)/i,
    analyze: analyzeForcedContinuity
  },
  {
    name: "Roach Motel",
    description: "Easy to get in, difficult to get out - hiding logout or account deletion options",
    regex: /(logout|sign.*out|exit|leave).*(hide|obscure|difficult|hard)/i,
    analyze: analyzeRoachMotel
  },
  {
    name: "Privacy Zuckering",
    description: "Tricks users into sharing more information than they intended",
    regex: /(share|public|visible).*(default|automatic|trick|deceive)/i,
    analyze: analyzePrivacyZuckering
  },
  {
    name: "Bait and Switch",
    description: "Advertises one thing but delivers something different",
    regex: /(offer|deal|promotion).*(different|change|surprise|unexpected)/i,
    analyze: analyzeBaitAndSwitch
  },
  {
    name: "Confirmshaming",
    description: "Uses guilt-inducing language to manipulate user choices",
    regex: /(no|decline|cancel|skip).*(sorry|disappointed|sad|guilt|shame)/i,
    analyze: analyzeConfirmshaming
  },
  {
    name: "Disguised Ads",
    description: "Presents advertisements as regular content or recommendations",
    regex: /(advertisement|ad|sponsored|promoted).*(content|recommendation|regular)/i,
    analyze: analyzeDisguisedAds
  },
  {
    name: "Misdirection",
    description: "Designs interfaces to guide users toward unintended actions",
    regex: /(button|click|action).*(unintended|mislead|trick|deceive)/i,
    analyze: analyzeMisdirection
  },
  {
    name: "Scarcity/Urgency Manipulation",
    description: "Creates false urgency or artificial scarcity to pressure users",
    regex: /(limited|scarcity|urgency|countdown|timer).*(fake|artificial|pressure)/i,
    analyze: analyzeScarcityUrgency
  },
  {
    name: "Trick Questions",
    description: "Uses confusing or misleading language in forms and questions",
    regex: /(question|form).*(confusing|misleading|trick|deceive)/i,
    analyze: analyzeTrickQuestions
  },
  {
    name: "Preselected Options",
    description: "Pre-selects options that benefit the company rather than the user",
    regex: /(preselected|default|checked).*(true|yes|opt.*in)/i,
    analyze: analyzePreselectedOptions
  },
  {
    name: "Friend Spam",
    description: "Tricks users into inviting friends or sharing contacts without clear consent",
    regex: /(invite|share|friend|contact).*(without.*consent|trick|deceive)/i,
    analyze: analyzeFriendSpam
  },
  {
    name: "Fake Social Proof",
    description: "Uses fake reviews, testimonials, or statistics to manipulate users",
    regex: /(review|testimonial|rating|statistic).*(fake|artificial|manipulate)/i,
    analyze: analyzeFakeSocialProof
  },
  {
    name: "Obscured Unsubscribe",
    description: "Makes it difficult to unsubscribe from emails or notifications",
    regex: /(unsubscribe|opt.*out).*(difficult|hide|obscure|trap)/i,
    analyze: analyzeObscuredUnsubscribe
  },
  {
    name: "Missing Account Deletion",
    description: "No clear way for users to delete their account, making it difficult to leave the service",
    regex: /(settings|account|profile|preferences|user)/i,
    analyze: analyzeMissingAccountDeletion
  }
];
