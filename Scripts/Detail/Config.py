#!/bin/echo "This module must be imported by other Python scripts."

import os, platform, configparser

import Detail.Utility as utility


class Configuration( configparser.ConfigParser ):

   # Constructor
   def __init__( self, configPath ):

      super().__init__( dict_type = dict, allow_no_value = True )

      self.read( configPath )

      self.__validateToplevelPath()
      self.__validateConfigPaths()

   # Validation
   def __validateToplevelPath( self ):

      utility.printHeading( "Git configuration..." )

      upstreamURL  = self.get( "Common", "upstreamURL" )
      queriedURL   = utility.runCommandAndPipeStdout( "git config --get remote.origin.url" )
      toplevelPath = utility.runCommandAndPipeStdout( "git rev-parse --show-toplevel" )

      utility.printItem( "toplevelPath: ", toplevelPath )
      utility.printItem( "upstreamURL: ", upstreamURL )
      utility.printItem( "queriedURL: ", queriedURL )

      if not os.path.exists( toplevelPath ):
         utility.printError( "Git top level path does not exist: " + toplevelPath )
         raise SystemExit( 1 )

      if queriedURL != upstreamURL:
         utility.printError( "The upstream URL at the current working directory does not match project upstream URL: " + queriedURL )
         raise SystemExit( 1 )

      self.set( "Common", "toplevelPath", toplevelPath )

   def __validateConfigPath( self, sectionName, pathName, mustExist = True, isInternal = True ):

      path = self.get( sectionName, pathName, fallback = None )

      if path == None:
         utility.printError( "Configuration '" + section + "." + name + "' was not defined." )
         raise SystemExit( 1 )

      if isInternal:
         toplevelPath = self.get( "Common", "toplevelPath" )
         path = utility.joinPath( toplevelPath, path )
         prefixPath = os.path.commonprefix( [ toplevelPath, path ] )

         if not os.path.samefile( toplevelPath, prefixPath ):
            utility.printError( "Path was not resolved within top-level path scope: " + path )
            raise SystemExit( 1 )

         self.set( sectionName, pathName, path )

      utility.printItem( pathName + ": ", path )

      if not os.path.exists( path ):
         if mustExist:
            utility.printError( "Required path does not exist: " + path )
            raise SystemExit( 1 )
         else:
            utility.printWarning( "Path does not exist: " + path )

   def __validateConfigPaths( self ):

      utility.printHeading( "Path configuration..." )

      self.__validateConfigPath( "Common", "synergyCorePath" )
      self.__validateConfigPath( "Common", "synergyBuildPath", mustExist = False )
      self.__validateConfigPath( "Common", "binariesPath" )
      self.__validateConfigPath( "Common", "toolsPath" )

      if platform.system() == "Windows":
         self.__validateConfigPath( "Windows", "libQtPath", isInternal = False )
         self.__validateConfigPath( "Windows", "vcvarsallPath", isInternal = False )
      elif platform.system() == "Darwin":
         self.__validateConfigPath( "Darwin", "libQtPath", isInternal = False )

   # Convenience accessors
   def toplevelPath( self ):

      return self.get( "Common", "toplevelPath" )

   def synergyCorePath( self ):

      return self.get( "Common", "synergyCorePath" )

   def synergyBuildPath( self ):

      return self.get( "Common", "synergyBuildPath" )

   def binariesPath( self ):

      return self.get( "Common", "binariesPath" )

   def toolsPath( self ):

      return self.get( "Common", "toolsPath" )

   def libQtPath( self ):

      return self.get( platform.system(), "libQtPath" )

   def vcvarsallPath( self ):

      return self.get( platform.system(), "vcvarsallPath" )

   def cmakeGenerator( self ):

      return self.get( platform.system(), "cmakeGenerator" )

scriptPath = utility.joinPath( utility.basePathAtSource( __file__ ), ".." )
configPath = utility.joinPath( scriptPath, "config.txt" )

config = Configuration( configPath )
