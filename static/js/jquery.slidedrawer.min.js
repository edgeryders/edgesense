/*
 * jQuery Slide Drawer
 * Examples and documentation at: http://www.icastwork.com
 * Copyright (c) 2013 Isaac Castillo
 * Version: 0.1.1 (23-MAR-2013)
 * Licensed under the MIT license. https://github.com/icemancast/jquery-slide-drawer#license
 * Requires: jQuery v1.7.1 or later.
*/
;(function(e){var t={init:function(n,r){if(n.showDrawer==true&&n.slideTimeout==true){setTimeout(function(){t.slide(r,n.drawerHiddenHeight,n.slideSpeed)},n.slideTimeoutCount)}else if(n.showDrawer=="slide"){t.slide(r,n.drawerHiddenHeight,n.slideSpeed)}else if(n.showDrawer==false){t.hide(n,r)}e(".clickme").on("click",function(){t.toggle(n,r)})},toggle:function(n,r){e(r).height()+n.borderHeight===n.drawerHeight?t.slide(r,n.drawerHiddenHeight,n.slideSpeed):t.slide(r,n.drawerHeight-n.borderHeight,n.slideSpeed)},slide:function(t,n,r){e(t).animate({height:n},r)},hide:function(t,n){e(n).css("height",t.drawerHiddenHeight)}};e.fn.slideDrawer=function(n){var r=this.children(".drawer-content"),i=parseInt(r.css("border-top-width"));drawerHeight=this.height()+i;drawerContentHeight=r.height()-i;drawerHiddenHeight=drawerHeight-drawerContentHeight;var s={showDrawer:"slide",slideSpeed:700,slideTimeout:true,slideTimeoutCount:5e3,drawerContentHeight:drawerContentHeight,drawerHeight:drawerHeight,drawerHiddenHeight:drawerHiddenHeight,borderHeight:i};var n=e.extend(s,n);return this.each(function(){t.init(n,this)})}})(jQuery);